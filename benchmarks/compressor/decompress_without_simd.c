// Stub to link against zlib-ng without SIMD
//

#include <stdint.h>
#include <zlib-ng.h>
#include "run.h"
#include <sys/time.h>

void* decompress_without_SIMD(void* arg){
  struct decompress_args args = *((struct decompress_args*) (arg));

  struct timeval decompress_time_start;
  struct timeval decompress_time_end; 
  int err1 = gettimeofday(&decompress_time_start, NULL);
  args.err = zng_uncompress(args.dest, &args.dest_len, args.source, args.source_len);
  int err2 = gettimeofday(&decompress_time_end, NULL);
  if (err1 || err2){ args.err = 1; }
  else {
    args.time_taken = decompress_time_end.tv_sec + decompress_time_end.tv_usec / 1000000.0 - (decompress_time_start.tv_sec + decompress_time_start.tv_usec / 1000000.0);
  }
  return NULL;
 
}
//int32_t decompress_without_SIMD(uint8_t* dest, size_t* destLen, const uint8_t* source, size_t* sourceLen){
//  return zng_uncompress2(dest, destLen, source, sourceLen);
//}
