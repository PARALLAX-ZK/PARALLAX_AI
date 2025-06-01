use anchor_lang::prelude::*;
use crate::state::{TaskRequest, TaskCounter};

#[derive(Accounts)]
pub struct TriggerInference<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + TaskRequest::SIZE,
        seeds = [b"task", counter.count.to_be_bytes().as_ref()],
        bump
    )]
    pub task: Account<'info, TaskRequest>,

    #[account(mut)]
    pub user: Signer<'info>,

    #[account(
        mut,
        seeds = [b"task_counter"],
        bump
    )]
    pub counter: Account<'info, TaskCounter>,

    pub system_program: Program<'info, System>,
}

pub fn trigger_inference_handler(
    ctx: Context<TriggerInference>,
    model_id: String,
    input_data: String,
) -> Result<()> {
    require!(model_id.len() < 64, ErrorCode::ModelTooLong);
    require!(input_data.len() < 256, ErrorCode::InputTooLong);

    let task = &mut ctx.accounts.task;
    let counter = &mut ctx.accounts.counter;

    task.user = *ctx.accounts.user.key;
    task.model_id = model_id.clone();
    task.input_data = input_data.clone();
    task.timestamp = Clock::get()?.unix_timestamp;
    task.task_id = counter.count;

    counter.count += 1;

    emit!(InferenceTriggered {
        user: task.user,
        model_id,
        task_id: task.task_id,
        input_preview: input_data.get(..40).unwrap_or("").to_string()
    });

    msg!("New inference request recorded: task_id = {}", task.task_id);

    Ok(())
}

#[event]
pub struct InferenceTriggered {
    pub user: Pubkey,
    pub model_id: String,
    pub task_id: u64,
    pub input_preview: String,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Model ID is too long")]
    ModelTooLong,
    #[msg("Input data is too long")]
    InputTooLong,
}
