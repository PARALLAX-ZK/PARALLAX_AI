use anchor_lang::prelude::*;
use crate::state::TaskRequest;

#[derive(Accounts)]
pub struct TriggerInference<'info> {
    #[account(init, payer = user, space = 8 + TaskRequest::SIZE)]
    pub task: Account<'info, TaskRequest>,

    #[account(mut)]
    pub user: Signer<'info>,

    #[account(
        seeds = [b"task_counter"],
        bump,
        init_if_needed,
        payer = user,
        space = 8 + 8
    )]
    pub counter: Account<'info, TaskCounter>,

    pub system_program: Program<'info, System>,
}

#[account]
pub struct TaskCounter {
    pub count: u64,
}

impl TaskRequest {
    pub const SIZE: usize = 32 + 64 + 64 + 8 + 8;
}

pub fn trigger_inference_handler(
    ctx: Context<TriggerInference>,
    model_id: String,
    input_data: String,
) -> Result<()> {
    let task = &mut ctx.accounts.task;
    let counter = &mut ctx.accounts.counter;

    task.user = *ctx.accounts.user.key;
    task.model_id = model_id;
    task.input_data = input_data;
    task.timestamp = Clock::get()?.unix_timestamp;
    task.task_id = counter.count;

    counter.count += 1;

    emit!(InferenceTriggered {
        user: *ctx.accounts.user.key,
        model_id: task.model_id.clone(),
        task_id: task.task_id,
    });

    msg!(" Triggered offchain inference: task {}", task.task_id);
    Ok(())
}

#[event]
pub struct InferenceTriggered {
    pub user: Pubkey,
    pub model_id: String,
    pub task_id: u64,
}
