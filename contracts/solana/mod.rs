use anchor_lang::prelude::*;
use crate::instructions::*;

pub mod instructions;
pub mod state;
pub mod utils;

declare_id!("PRLX1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");

#[program]
pub mod parallax_solana {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("✅ Parallax smart contract initialized");
        Ok(())
    }

    pub fn trigger_inference(
        ctx: Context<TriggerInference>,
        model_id: String,
        input_data: String,
    ) -> Result<()> {
        trigger_inference_handler(ctx, model_id, input_data)
    }

    pub fn submit_dacert(
        ctx: Context<SubmitDACert>,
        task_id: String,
        output_hash: String,
        signatures: Vec<[u8; 64]>,
        signers: Vec<Pubkey>,
    ) -> Result<()> {
        submit_dacert_handler(ctx, task_id, output_hash, signatures, signers)
    }
}
