use anchor_lang::prelude::*;

#[account]
pub struct TaskRequest {
    pub user: Pubkey,
    pub model_id: String,     // e.g. "parallax-llm-v1"
    pub input_data: String,   // e.g. prompt or image URI
    pub timestamp: i64,
    pub task_id: u64,
}

#[account]
pub struct VerifiedResult {
    pub task_id: String,
    pub output_hash: String,   // SHA256 of the result payload
    pub timestamp: i64,
    pub signers: Vec<Pubkey>,  // Public keys of validators
}

impl TaskRequest {
    pub const SIZE: usize = 
        32 +       // user pubkey
        4 + 64 +   // model_id string
        4 + 256 +  // input_data string
        8 +        // timestamp
        8;         // task_id
}

impl VerifiedResult {
    pub const SIZE: usize = 
        4 + 64 +   // task_id
        4 + 64 +   // output_hash
        8 +        // timestamp
        4 + (32 * 5); // up to 5 validator pubkeys
}
