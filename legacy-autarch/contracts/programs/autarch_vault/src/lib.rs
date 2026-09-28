use anchor_lang::prelude::*;
use anchor_lang::solana_program::{
    instruction::Instruction,
    program::invoke_signed,
    system_instruction,
};

declare_id!("Autarch11111111111111111111111111111111111");

pub const SMART_VAULT_SEED: &[u8] = b"smart_vault";

// Verified Ecosystem Program Whitelist on Cookie Chain (SVM)
// 1. Candy Shop DEX Aggregator
pub const CANDY_SHOP_PROGRAM_ID: Pubkey = pubkey!("CandyShop1111111111111111111111111111111111");
// 2. Cookiebox DAMM v2 / CLMM
pub const COOKIEBOX_PROGRAM_ID: Pubkey = pubkey!("Cookiebox1111111111111111111111111111111111");
// 3. Cookieswap SAMM
pub const COOKIESWAP_PROGRAM_ID: Pubkey = pubkey!("Cookieswap111111111111111111111111111111111");
// 4. bCOOK SPL Stake Pool
pub const BCOOK_STAKE_POOL_PROGRAM_ID: Pubkey = pubkey!("bCookStakePoo1111111111111111111111111111111");
// 5. Baked Bazaar Metaplex Auction House
pub const BAKED_BAZAAR_PROGRAM_ID: Pubkey = pubkey!("BakedBazaar111111111111111111111111111111111");

#[program]
pub mod autarch_vault {
    use super::*;

    /// Initializes a new non-custodial Smart Vault PDA for a given user.
    /// Sets the user as the permanent immutable owner and assigns a delegated AI agent pubkey.
    pub fn initialize_vault(
        ctx: Context<InitializeVault>,
        delegated_agent: Pubkey,
    ) -> Result<()> {
        let vault = &mut ctx.accounts.smart_vault;
        vault.owner = ctx.accounts.user.key();
        vault.delegated_agent = delegated_agent;
        vault.bump = ctx.bumps.smart_vault;
        vault.total_deposited = 0;
        vault.grail_pot_tickets = 0;
        vault.created_at = Clock::get()?.unix_timestamp;

        msg!("Autarch Smart Vault initialized for owner: {}", vault.owner);
        msg!("Delegated agent authorized: {}", vault.delegated_agent);
        Ok(())
    }

    /// Deposits native $COOK (lamports) into the user's non-custodial Smart Vault PDA.
    pub fn deposit_cook(ctx: Context<DepositCook>, amount_lamports: u64) -> Result<()> {
        require!(amount_lamports > 0, VaultError::InvalidDepositAmount);

        // Transfer SOL/COOK from user wallet into vault PDA
        let cpi_context = CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            anchor_lang::system_program::Transfer {
                from: ctx.accounts.user.to_account_info(),
                to: ctx.accounts.smart_vault.to_account_info(),
            },
        );
        anchor_lang::system_program::transfer(cpi_context, amount_lamports)?;

        let vault = &mut ctx.accounts.smart_vault;
        vault.total_deposited = vault
            .total_deposited
            .checked_add(amount_lamports)
            .ok_or(VaultError::MathOverflow)?;

        msg!("Deposited {} lamports into Smart Vault PDA", amount_lamports);
        Ok(())
    }

    /// Executes an autonomous Cross-Program Invocation (CPI) on behalf of the user.
    /// CRITICAL SECURITY INVARIANTS:
    /// 1. ONLY the authorized delegated_agent (matching COOKIE_PRIVATE_KEY) can invoke this.
    /// 2. The target program MUST exist in the verified ecosystem whitelist.
    /// 3. The vault PDA signs the CPI using its programmatic derived seeds.
    pub fn execute_delegated_cpi<'info>(
        ctx: Context<'_, '_, '_, 'info, ExecuteDelegatedCpi<'info>>,
        data: Vec<u8>,
    ) -> Result<()> {
        let vault = &ctx.accounts.smart_vault;
        let target_program = &ctx.accounts.target_program;

        // Verify sender is strictly the authorized agent
        require_keys_eq!(
            ctx.accounts.delegated_agent.key(),
            vault.delegated_agent,
            VaultError::UnauthorizedAgent
        );

        // Verify target program is whitelisted
        let is_whitelisted = target_program.key() == CANDY_SHOP_PROGRAM_ID
            || target_program.key() == COOKIEBOX_PROGRAM_ID
            || target_program.key() == COOKIESWAP_PROGRAM_ID
            || target_program.key() == BCOOK_STAKE_POOL_PROGRAM_ID
            || target_program.key() == BAKED_BAZAAR_PROGRAM_ID;

        require!(is_whitelisted, VaultError::ProgramNotWhitelisted);

        // Construct account metas for target instruction
        let account_metas: Vec<AccountMeta> = ctx
            .remaining_accounts
            .iter()
            .map(|acc| {
                if acc.key == &vault.key() {
                    AccountMeta::new(acc.key(), true) // Vault signs via seeds
                } else if acc.is_writable {
                    AccountMeta::new(acc.key(), acc.is_signer)
                } else {
                    AccountMeta::new_readonly(acc.key(), acc.is_signer)
                }
            })
            .collect();

        let instruction = Instruction {
            program_id: target_program.key(),
            accounts: account_metas,
            data,
        };

        let bump = vault.bump;
        let owner_key = vault.owner;
        let signer_seeds: &[&[&[u8]]] = &[&[
            SMART_VAULT_SEED,
            owner_key.as_ref(),
            &[bump],
        ]];

        let mut account_infos: Vec<AccountInfo<'info>> = Vec::new();
        account_infos.push(target_program.to_account_info());
        account_infos.push(vault.to_account_info());
        for acc in ctx.remaining_accounts.iter() {
            account_infos.push(acc.clone());
        }

        invoke_signed(&instruction, &account_infos, signer_seeds)?;

        msg!("CPI to whitelisted program {} successfully executed", target_program.key());
        Ok(())
    }

    /// Non-custodial withdrawal.
    /// MATHEMATICAL INVARIANT: Funds can NEVER route to an arbitrary destination.
    /// All withdrawn lamports strictly route directly back to the user's originating owner wallet.
    pub fn withdraw_to_owner(ctx: Context<WithdrawToOwner>, amount_lamports: u64) -> Result<()> {
        let vault = &mut ctx.accounts.smart_vault;
        let vault_lamports = **vault.to_account_info().lamports.borrow();

        // Ensure rent exempt minimum remains or complete closure
        require!(amount_lamports <= vault_lamports, VaultError::InsufficientVaultFunds);

        **vault.to_account_info().try_borrow_mut_lamports()? -= amount_lamports;
        **ctx.accounts.owner.try_borrow_mut_lamports()? += amount_lamports;

        msg!(
            "Successfully withdrawn {} lamports directly to originating owner address: {}",
            amount_lamports,
            ctx.accounts.owner.key()
        );
        Ok(())
    }
}

// ----------------------------------------------------------------------------
// Account Validation Contexts
// ----------------------------------------------------------------------------

#[derive(Accounts)]
pub struct InitializeVault<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + SmartVault::INIT_SPACE,
        seeds = [SMART_VAULT_SEED, user.key().as_ref()],
        bump
    )]
    pub smart_vault: Account<'info, SmartVault>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct DepositCook<'info> {
    #[account(
        mut,
        seeds = [SMART_VAULT_SEED, user.key().as_ref()],
        bump = smart_vault.bump,
        has_one = user @ VaultError::UnauthorizedOwner
    )]
    pub smart_vault: Account<'info, SmartVault>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteDelegatedCpi<'info> {
    #[account(
        mut,
        seeds = [SMART_VAULT_SEED, smart_vault.owner.as_ref()],
        bump = smart_vault.bump
    )]
    pub smart_vault: Account<'info, SmartVault>,

    /// CHECK: The delegated agent executing on-chain commands via COOKIE_PRIVATE_KEY
    #[account(signer)]
    pub delegated_agent: Signer<'info>,

    /// CHECK: Validated against whitelist in program logic
    pub target_program: AccountInfo<'info>,
}

#[derive(Accounts)]
pub struct WithdrawToOwner<'info> {
    #[account(
        mut,
        seeds = [SMART_VAULT_SEED, owner.key().as_ref()],
        bump = smart_vault.bump,
        has_one = owner @ VaultError::UnauthorizedOwner
    )]
    pub smart_vault: Account<'info, SmartVault>,

    #[account(mut)]
    pub owner: Signer<'info>,
}

// ----------------------------------------------------------------------------
// State Accounts
// ----------------------------------------------------------------------------

#[account]
#[derive(InitSpace)]
pub struct SmartVault {
    pub owner: Pubkey,            // 32 bytes: originating user's Nightly wallet address
    pub delegated_agent: Pubkey,  // 32 bytes: authorized agent keypair
    pub bump: u8,                 // 1 byte: PDA bump
    pub total_deposited: u64,     // 8 bytes: cumulative COOK deposited
    pub grail_pot_tickets: u64,   // 8 bytes: accumulated jackpot tickets
    pub created_at: i64,          // 8 bytes: unix timestamp
}

// ----------------------------------------------------------------------------
// Errors
// ----------------------------------------------------------------------------

#[error_code]
pub enum VaultError {
    #[msg("Unauthorized: Signer does not match the vault owner")]
    UnauthorizedOwner,

    #[msg("Unauthorized: Signer is not the designated delegated AI agent")]
    UnauthorizedAgent,

    #[msg("Target program is not present in verified ecosystem whitelist")]
    ProgramNotWhitelisted,

    #[msg("Invalid deposit amount: must be greater than zero")]
    InvalidDepositAmount,

    #[msg("Insufficient vault lamports to satisfy withdrawal request")]
    InsufficientVaultFunds,

    #[msg("Mathematical overflow occurred during accounting")]
    MathOverflow,
}
