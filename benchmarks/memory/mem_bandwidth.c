#include <bits/types/struct_timeval.h>
#include <stdint.h>
#include <string.h>
#include <sys/times.h>
#include <sys/time.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <unistd.h>
#include <pthread.h>


long long int total = (long long)1024 * 1024 * 1024 * 64;

int get_num_cpu(){
  FILE* inp = popen("lscpu", "r");
  char* buf = NULL;
  size_t buf_size;
  while( getline(&buf, &buf_size, inp) != -1 ){
    if (strncmp(buf, "Core(s) per socket:", 19) == 0){
      char** temp = NULL;
      long real_cpus = strtol(buf + 26, temp, 10);
      free(buf);
      return real_cpus; 
    }
  }
  free(buf);
  return -1;
}
struct run_benchmark_thread_args {
  long long int iters;
  long long int size;
  struct timeval start;
  struct timeval end;
  uint64_t* arr;
};

void* run_benchmark_thread(void* void_args){
  struct run_benchmark_thread_args* args = (struct run_benchmark_thread_args*) void_args;
  int err1 = gettimeofday(&(args->start), NULL);
  //actual benchmark here
    for (long long int i = 0; (i < (args->iters)); i++){
      for (long long int j = 0; j < args->size/sizeof(uint64_t); j++){
        args->arr[j] = args->arr[j] + 1;
      }
    }
  int err2 = gettimeofday(&(args->end), NULL);
  return NULL;
}
void run_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size){
  long long iters = total / size;
  pthread_t threads[NUM_THREADS];
  struct run_benchmark_thread_args thread_args[NUM_THREADS];
  for (int i = 0; i < NUM_THREADS; i++) {
    uint64_t* arr = malloc(size/NUM_THREADS);
    thread_args[i] = (struct run_benchmark_thread_args) {iters, size/NUM_THREADS, 0};
    if (arr == NULL) { fprintf(stderr, "failed allocating memory"); exit(EXIT_FAILURE); }
    for (uint64_t i = 0; i < (size/NUM_THREADS) / sizeof(uint64_t); i++){
      arr[i] = i;
    } 
    thread_args[i].arr = arr;
  }
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_create(&threads[i], NULL, run_benchmark_thread, &thread_args[i])){
      fprintf(stderr, "Failed to create thread \n");
      exit(EXIT_FAILURE);
    }
  }
  double bandwidth = 0;
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_join(threads[i], NULL)){
      fprintf(stderr, "Failed joining thread\n");
    }
    fwrite(&(thread_args[i].arr[random() % (size/NUM_THREADS / sizeof(uint64_t))]), sizeof(uint64_t), 1, fnull);
    free(thread_args[i].arr);
    bandwidth += ((double)total/NUM_THREADS/1024/1024/1024)/(((thread_args[i].end.tv_sec * 1000000 + thread_args[i].end.tv_usec) - (thread_args[i].start.tv_sec * 1000000 + thread_args[i].start.tv_usec))/(double)1000000); 
    //printf("size: %lld, thread: %ld, cum_band: %lf\n", thread_args[i].size, threads[i], bandwidth );
  }
  fprintf(fout, "%lld,%lf \n", size/1024, bandwidth);
}

void check_and_run_cache(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size, int arr_size, uint64_t arr[arr_size]){
  int i = 0;
  while ( i < arr_size && arr[i] < size){ i++; }
  while ( i < arr_size && arr[i] < 2 * size){
    run_benchmark(NUM_THREADS, fout, fnull, arr[i]);
    i++;
  }
}
void sort_arr(int size, uint64_t arr[size]){
  for (int i = 0; i < size - 1; i++){
    uint64_t min = arr[i];
    for (int j = i + 1; j < size; j++){
      if (arr[j] < arr[i]){
        uint64_t temp = arr[j];
        arr[j] = arr[i];
        arr[i] = temp;
      }
    }
  }
}
long long int log2u(long long int num) {
  if (num == 0) { return 1; }
  long long int pos = 0;
  while (num > 0){
    pos++;
    num /= 2;
  }
  return pos;
}
long long int poweroftwo(long long int exp){
  if (exp == 0) { return 1; }
  long long int num = 2;
  while (exp - 1 > 0){
    num *= 2;
    exp--;
  }
  return num;
}
void merge_list(long long int pow2_size, long long pow2[pow2_size], long long int merge_size, unsigned long merge_lst[merge_size]) {
  long long int curr_pow_2 = poweroftwo(log2u(pow2[0]));
  //long long int pow2_index = 1;
  long long int merge_index = 0;
  while (merge_lst[merge_index] <= pow2[0] && merge_index < merge_size){
    merge_index++;
  }
  long long int i = 1;
  for (; i < pow2_size; i++){
    if (merge_index >= merge_size) { break; } 
    if (merge_lst[merge_index] < curr_pow_2) {
      pow2[i] = merge_lst[merge_index];
      merge_index++;
    }
    else {
      pow2[i] = curr_pow_2;
      curr_pow_2 *= 2;
    }
  }
  for (; i < pow2_size; i++){
    pow2[i] = curr_pow_2;
    curr_pow_2 *= 2;
  }
}
int main(int argc, const char** argv){
  if (argc != 6){
    fprintf(stderr, "invalid arguments: must be num threads (0 for max threads), starting size (in bytes) (power of 2), ending size (in bytes) (power of 2), length multipler (power of 2), output file\n");
    exit(EXIT_FAILURE);
  }

  char** temp = NULL;
  int NUM_THREADS = strtol(argv[1], temp, 10);
  if (NUM_THREADS == -1){ //experimental
    NUM_THREADS = get_num_cpu();
  }
  if (NUM_THREADS == 0){
    if (sysconf(_SC_NPROCESSORS_CONF) != sysconf(_SC_NPROCESSORS_CONF)) { fprintf(stderr, "found offline cpu\n"); }
    NUM_THREADS = sysconf(_SC_NPROCESSORS_CONF);  
  }
  if (NUM_THREADS == -1){
    fprintf(stderr, "failed to get thread count\n");
    exit(EXIT_FAILURE);
  }
  long long START_SIZE;
  if (strcmp(argv[2], "L1_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL1_DCACHE_SIZE); }
  else if (strcmp(argv[2], "L2_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL2_CACHE_SIZE); }
  else if (strcmp(argv[2], "L3_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL3_CACHE_SIZE); }
  else { START_SIZE = strtoll(argv[2], temp, 10); }
  long long END_SIZE;
  if (strcmp(argv[3], "L1_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL1_DCACHE_SIZE); }
  else if (strcmp(argv[3], "L2_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL2_CACHE_SIZE); }
  else if (strcmp(argv[3], "L3_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL3_CACHE_SIZE); }
  else { END_SIZE = strtoll(argv[3], temp, 10); }
  total = strtoll(argv[4], temp, 10) * total;
  uint64_t cache_sizes[9];
  cache_sizes[0] = sysconf(_SC_LEVEL1_DCACHE_SIZE);
  cache_sizes[1] = sysconf(_SC_LEVEL2_CACHE_SIZE);
  cache_sizes[2] = cache_sizes[0] * NUM_THREADS;
  cache_sizes[3] = cache_sizes[1] * NUM_THREADS;
  cache_sizes[4] = cache_sizes[2] / 2;
  cache_sizes[5] = cache_sizes[3] / 2;
  if (sysconf(_SC_LEVEL3_CACHE_SIZE) != -1) {
    cache_sizes[6] = sysconf(_SC_LEVEL3_CACHE_SIZE);
    cache_sizes[7] = cache_sizes[6] * NUM_THREADS;
    cache_sizes[8] = cache_sizes[7] / 2;
  }
  else { 
    cache_sizes[6] = INT64_MAX;
    cache_sizes[7] = INT64_MAX;
    cache_sizes[8] = INT64_MAX;
  }
  sort_arr(sizeof(cache_sizes)/ sizeof(uint64_t), cache_sizes);
  
  FILE* fout = fopen(argv[5], "w");
  FILE* fnull = fopen("/dev/null", "w");

  fprintf(fout, "working set size (kB), Average throughput (GB/s) \n");
   
  if ( START_SIZE == END_SIZE ) {
    run_benchmark(NUM_THREADS, fout, fnull, START_SIZE);
    exit(EXIT_SUCCESS);
  }
  long long int sizes_size = log2u(END_SIZE / START_SIZE) + 2 + 9;
  long long int* sizes = malloc(sizes_size * sizeof(long long int));
  sizes[0] = START_SIZE;
  merge_list( sizes_size, sizes, 9, cache_sizes);
  for (int i = 0; sizes[i] < END_SIZE && i < log2u(END_SIZE/ START_SIZE) + 2 + 9; i++)
    run_benchmark(NUM_THREADS, fout, fnull, sizes[i]);
  run_benchmark(NUM_THREADS, fout, fnull, END_SIZE);

  //run_benchmark(NUM_THREADS, fout, fnull, START_SIZE);
  //check_and_run_cache(NUM_THREADS, fout, fnull, START_SIZE, sizeof(cache_sizes) / sizeof(uint64_t), cache_sizes);
  //for (long long int size = 1024; size < END_SIZE; size *= 2){
  //  if (size <= START_SIZE) { continue; }
  //  run_benchmark(NUM_THREADS, fout, fnull, size);
  //  check_and_run_cache(NUM_THREADS, fout, fnull, size, sizeof(cache_sizes) / sizeof(uint64_t), cache_sizes);
  //}
  exit(EXIT_SUCCESS);
}
