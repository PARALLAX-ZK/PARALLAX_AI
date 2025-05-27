use anchor_lang::prelude::*;

/// Verifies that a quorum of validators have signed a message.
/// In production, this would call into a syscall or use Solana's `ed25519_program`.
pub fn verify_signatures(
    task_id: &str,
    output_hash: &str,
    signatures: &[ [u8; 64] ],
    signers: &[Pubkey],
) -> bool {
    // Simulate a minimum threshold
    let quorum = 3;

    if signatures.len() < quorum || signers.len() < quorum {
        return false;
    }

    // Simulated message: concat of task ID + output hash
    let message = format!("{}:{}", task_id, output_hash);
    let _message_bytes = message.as_bytes();

    // NOTE:
    // Here you would normally verify:
    // ed25519_verify(message_bytes, signature, pubkey)
    // using ed25519_program or CPI into a verification oracle.

    // For now, simulate "passed" if lengths match and quorum is met
    true
}
