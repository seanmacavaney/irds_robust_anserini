import io

# A very basic python port of Lucene StoredFields format.

MAGIC = 0x3fd76c17
FOOTER_MAGIC = ~MAGIC

def read_vint(f):
  result = 0
  inp = 128
  idx = 0
  while inp & 128 != 0:
    inp = f.read(1)[0]
    result += (inp & 127) << (7 * idx)
    idx += 1
  return result

def read_uint32(f):
  return int.from_bytes(f.read(4), 'big')

def read_uint64(f):
  return int.from_bytes(f.read(8), 'big')

def verify_magic(f):
  assert read_uint32(f) == MAGIC

def read_string(f):
  length = read_vint(f)
  return f.read(length).decode('utf8')

def read_suffix(f):
  length = f.read(1)[0]
  return f.read(length)

def read_zfloat(f):
  b = f.read(1)[0]
  if b == 0xFF:
    return float(read_uint32(f))
  elif (b & 0x80) != 0:
    return (b & 0x7f) - 1
  f.read(3)
  return 0

def decompress_lz4(compressed, decompressedLen):
  MIN_MATCH = 4
  result = bytearray()
  destEnd = decompressedLen

  while len(result) < destEnd:
      # literals
      token = compressed.read(1)[0]
      literalLen = token >> 4

      if (literalLen != 0):
        if (literalLen == 0x0F):
          l = 0
          last_l = compressed.read(1)[0]
          while last_l == 0xFF:
            literalLen += 0xFF
            last_l = compressed.read(1)[0]
          literalLen += last_l
        result += compressed.read(literalLen)

      if len(result) >= destEnd:
        break

      # matchs
      matchDec = int.from_bytes(compressed.read(2), 'little')
      assert matchDec > 0

      matchLen = token & 0x0F
      if (matchLen == 0x0F):
        l = 0
        last_l = compressed.read(1)[0]
        while last_l == 0xFF:
          matchLen += 0xFF
          last_l = compressed.read(1)[0]
        matchLen += last_l
      matchLen += MIN_MATCH

      ref = len(result) - matchDec
      end = len(result) + matchLen
      while len(result) < end:
        result += result[ref:ref+1]
        ref += 1
  return result


def byte_count(bits_per_doc, num_docs):
  bit_count = bits_per_doc * num_docs
  if bit_count % 8 == 0:
    return bit_count // 8, 0
  return bit_count // 8 + 1, 8 - bit_count % 8


def stored_fields_iter(path):
  with open(path, 'rb') as file:
    verify_magic(file)
    codec = read_string(file)
    version = read_uint32(file)
    objectId = file.read(16)
    suffix = read_suffix(file)
    chunk_size = read_vint(file)
    packed_ints_version = read_vint(file)
    while True:
      if int.from_bytes(file.peek(4), 'big') == FOOTER_MAGIC:
        break
      doc_base = read_vint(file)
      buf_doc = read_vint(file)
      num_docs = buf_doc >> 1
      sliced = (buf_doc & 1) == 1
      if num_docs == 1:
        num_stored_fields = [read_vint(file)]
        doc_lens = [read_vint(file)]
      else:
        count = read_vint(file)
        if count == 0:
          num_stored_fields = [read_vint(file)] * num_docs
        else:
          cnt, wasted = byte_count(count, num_docs)
          num_stored_int = int.from_bytes(file.read(cnt), 'big') >> wasted
          num_stored_fields = []
          for _ in range(num_docs):
            num_stored_fields.append(num_stored_int & (2**count-1))
            num_stored_int = num_stored_int >> count
        if not file.peek():
          break
        count = read_vint(file)
        if count == 0:
          doc_lens = [read_vint(file)] * num_docs
        else:
          cnt, wasted = byte_count(count, num_docs)
          doc_lens_int = int.from_bytes(file.read(cnt), 'big') >> wasted
          doc_lens = []
          for _ in range(num_docs):
            doc_lens.append(doc_lens_int & (2**count-1))
            doc_lens_int = doc_lens_int >> count
          assert doc_lens_int == 0
      if sliced:
        fields = io.BytesIO()
        while fields.tell() < sum(doc_lens):
          size = min(sum(doc_lens) - fields.tell(), chunk_size)
          fields.write(decompress_lz4(file, size))
        fields.seek(0)
      else:
        fields = io.BytesIO(decompress_lz4(file, sum(doc_lens)))
      for field_count, field_len in zip(num_stored_fields, doc_lens):
        out_fields = {}
        for _ in range(field_count):
          field_type = read_vint(fields)
          ftype = field_type & 0x07
          field_idx = field_type >> 3
          if ftype == 0:
            out_fields[field_idx] = read_string(fields)
          else:
            raise ValueError(ftype)
        yield out_fields
