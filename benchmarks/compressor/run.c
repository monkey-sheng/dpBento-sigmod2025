//#include <bits/pthreadtypes.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <zlib-ng.h>
#include <stdbool.h>
#include "run.h"
//#include "structs.c"
#include "decompress_with_simd.c"
#include "decompress_without_simd.c"
#include "decompres_with_doca.c"

// For now, we make each thread run the same commpression job

/* Assumes that elements in output == num_files
 * */
int openFiles(int num_files, char** filenames, FILE** output){
  for (int i = 0; i < num_files; i++){
    output[i] = fopen(filenames[i], "r");
    if (output[i] == NULL) { return NULL; }
  } 
}

int write_stats(FILE* output_file, int NUM_THREADS, struct decompress_args thread_outputs[NUM_THREADS], char* decompression_setting){
  char* type;
  if (strcmp(decompression_setting, "1") == 0){ type = "without_SIMD"; }
  else if (strcmp(decompression_setting, "2") == 0) { type = "with_SIMD"; }
  else if (strcmp(decompression_setting, "3") == 0) { type = "DOCA"; }
  int err;
  for (int i = 0; i < NUM_THREADS; i++){
    if (fprintf(output_file, "%s,%i,%lf", type, i, thread_outputs[i].time_taken) < 0){
      fprintf(stderr, "Error writing to output file");
      exit(1);
    }
  }
}



int main(int argc, char** argv) {
  int NUM_THREADS = 1;
  void* (*decompress_func)(void* arg); 
  FILE* stats_file;
  if (argc != 4) {
    fprintf(stderr, "invalid arguments: must be compression type, num threads (-1 for max), file to compress, output stats file");
    if (strcmp(argv[2], "-1") == 0) {
      NUM_THREADS = sysconf(_SC_NPROCESSORS_CONF);
      if (NUM_THREADS == 1) { 
        fprintf(stderr, "Failed to get number of threads");
        //NOTE: maybe default to 1 instead?
        exit(1);
      }
    }
    else {
        char** temp = NULL;
        NUM_THREADS = strtol(argv[2], temp, 10); 
    }

    if (strcmp(argv[1], "1")){ decompress_func = decompress_without_SIMD;}
    else if (strcmp(argv[1], "2")){ decompress_func = decompress_with_SIMD;}
    else if (strcmp(argv[1], "3")){ decompress_func = decompress_with_DOCA;}
    else {
      fprintf(stderr, "Invalid option for decompression type");
      exit(1);
    }
    
    stats_file = fopen(argv[4], "a");
  }
  FILE* file = fopen(argv[3], "r");
  if (file == NULL) {
    fprintf(stderr, "Couldn't open all files");
    exit(1);
  }
  pthread_t threads[NUM_THREADS];
  struct decompress_args thread_args[NUM_THREADS];
  struct stat st;
  fstat(fileno(file), &st);
  uint8_t* source_buf = malloc(st.st_size);
  if (fread(source_buf, sizeof(uint8_t), st.st_size, file)){ 
    fprintf(stderr, "Failed to write source file to buffer");
    exit(1); 
  }
  for (int i = 0; i < NUM_THREADS; i++){
    uint8_t* output_buf = malloc(2 * st.st_size); // a bit high, but *should* work 
    thread_args[i] = (struct decompress_args) {output_buf, 2 * st.st_size, source_buf, st.st_size,};
    if (pthread_create(&threads[i], NULL, decompress_func, &thread_args[i])){
      fprintf(stderr, "Failed to create thread");
      exit(1);
    }
  }
  for (int i = 0; i < NUM_THREADS; i++){
    pthread_join(threads[i], NULL);
  }

  write_stats(stats_file, NUM_THREADS, thread_args, argv[1]);
  exit(0);


  // for thread, share source buf
  // alloc separate dest buf
  // decompress into dest buf, with time
  // and free everything
  // move to next file
  
}
