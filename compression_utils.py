import gzip
import zlib
import base64
import logging
from typing import Union

logger = logging.getLogger("COMPRESSION_UTILS")

def compress_gzip(data: Union[str, bytes]) -> bytes:
    """
    Compresses data using gzip.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    try:
        compressed = gzip.compress(data)
        return compressed
    except Exception as e:
        logger.error(f"GZIP compression failed: {e}")
        raise

def decompress_gzip(data: bytes) -> str:
    """
    Decompresses gzip-compressed data and returns it as UTF-8 string.
    """
    try:
        decompressed = gzip.decompress(data)
        return decompressed.decode("utf-8")
    except Exception as e:
        logger.error(f"GZIP decompression failed: {e}")
        raise

def compress_zlib(data: Union[str, bytes]) -> bytes:
    """
    Compresses data using zlib.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    try:
        return zlib.compress(data)
    except Exception as e:
        logger.error(f"ZLIB compression failed: {e}")
        raise

def decompress_zlib(data: bytes) -> str:
    """
    Decompresses zlib-compressed data.
    """
    try:
        return zlib.decompress(data).decode("utf-8")
    except Exception as e:
        logger.error(f"ZLIB decompression failed: {e}")
        raise

def encode_base64(data: bytes) -> str:
    """
    Encodes compressed binary data into a base64 string.
    """
    try:
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        logger.error(f"Base64 encoding failed: {e}")
        raise

def decode_base64(data: str) -> bytes:
    """
    Decodes a base64 string back into binary data.
    """
    try:
        return base64.b64decode(data.encode("utf-8"))
    except Exception as e:
        logger.error(f"Base64 decoding failed: {e}")
        raise

def compress_for_transport(data: str, method: str = "gzip-base64") -> str:
    """
    Compresses and encodes data for transport over JSON or calldata.
    Supports 'gzip-base64' and 'zlib-base64'.
    """
    if method == "gzip-base64":
        return encode_base64(compress_gzip(data))
    elif method == "zlib-base64":
        return encode_base64(compress_zlib(data))
    else:
        raise ValueError("Unsupported compression method")

def decompress_from_transport(data: str, method: str = "gzip-base64") -> str:
    """
    Decodes and decompresses transport-encoded data.
    """
    if method == "gzip-base64":
        return decompress_gzip(decode_base64(data))
    elif method == "zlib-base64":
        return decompress_zlib(decode_base64(data))
    else:
        raise ValueError("Unsupported decompression method")

# Example usage
if __name__ == "__main__":
    text = "The quick brown fox jumps over the lazy dog."
    print("Original:", text)
    c = compress_for_transport(text)
    print("Compressed (gzip+base64):", c[:50], "...")
    d = decompress_from_transport(c)
    print("Decompressed:", d)
