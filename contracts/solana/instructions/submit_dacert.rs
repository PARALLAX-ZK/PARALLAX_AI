use anchor_lang::prelude::*;
use crate::state::VerifiedResult;
use crate::utils::verify_signatures;

#[derive(Accounts)]
pub struct SubmitDACert<'info> {
    #[account(init, payer = user, space = 8 + VerifiedResult::SIZE, seeds = [b"result", task_id.as_bytes()], bump)]
    pub verified: Account<'info, VerifiedResult>,

    #[account(mut)]
    pub user: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn submit_dacert_handler(
    ctx: Context<SubmitDACert>,
    task_id: String,
    output_hash: String,
    signatures: Vec<[u8; 64]>,
    signers: Vec<Pubkey>,
) -> Result<()> {
    let verified = &mut ctx.accounts.verified;

    // Verify quorum of committee signatures
    require!(
        verify_signatures(&task_id, &output_hash, &signatures, &signers),
        ErrorCode::InvalidDACert
    );

    verified.task_id = task_id;
    verified.output_hash = output_hash;
    verified.timestamp = Clock::get()?.unix_timestamp;
    verified.signers = signers;

    emit!(DACertVerified {
        task_id: verified.task_id.clone(),
        output_hash: verified.output_hash.clone(),
    });

    msg!(" DACert verified and result committed to Solana");
    Ok(())
}

#[event]
pub struct DACertVerified {
    pub task_id: String,
    pub output_hash: String,
}

#[error_code]
pub enum ErrorCode {
    #[msg("DACert signature verification failed.")]
    InvalidDACert,
}
