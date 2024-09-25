#include <stdint.h>
#include <sys/types.h>
#include <stdint.h>

struct decompress_args {
  uint8_t* dest;
  size_t dest_len;
  const uint8_t* source;
  size_t source_len;
  int32_t err;
  double time_taken; 
};
