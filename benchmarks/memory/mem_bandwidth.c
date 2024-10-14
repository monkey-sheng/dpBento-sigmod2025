//#include <bits/types/cookie_io_functions_t.h>
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
#include <stdbool.h>


long long int total = (long long)1024 * 1024 * 1024 * 64;

enum pattern {
  RAND_READ,
  SEQ_READ,
  RAND_WRITE, //TODO
  SEQ_WRITE,
};

struct biguint{
  uint64_t num;
  uint64_t padding[7];
}typedef biguint;

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
struct benchmark_thread_args {
  long long int iters;
  long long int size;
  uint64_t counter;
  struct timeval start;
  struct timeval end;
  biguint* arr;
  uint32_t* rand_num_arr;
  uint64_t rand_num_arr_size;

};

void* run_read_benchmark_thread(void* void_args){
  struct benchmark_thread_args* args = (struct benchmark_thread_args*) void_args;
  uint64_t next = 0;
  int err1 = gettimeofday(&(args->start), NULL);
  //actual benchmark here
  for (long long int i = 0; (i < (args->iters)); i++){
    for (long long int j = 0; j < args->size/sizeof(biguint); j++){
      next = args->arr[next].num;
    }
  }
  int err2 = gettimeofday(&(args->end), NULL);
  if (err1 || err2) { fprintf(stderr, "failed to get time info"); }
  args->counter = next;
  return NULL;
}
bool arr_in(uint32_t num, int64_t num_elems, uint32_t elems[num_elems]){
  for (int i = 0; i < num_elems; i++){
    if (elems[i] == num){
      return true;
    }
  }
  return false;
}
void* run_write_rand_benchmark_thread(void* void_args){
  struct benchmark_thread_args* args = (struct benchmark_thread_args*) void_args;
  biguint* arr = args->arr;
  biguint to_push = (struct biguint) {0};

  int err1 = gettimeofday(&args->start, NULL);
  for (long long int i = 0; i < args->iters; i++){
    for (long long int j = 0; j < args->rand_num_arr_size; j++){
      args->arr[args->rand_num_arr[j]] = to_push;
    }
  }
  int err2 = gettimeofday(&args->end, NULL);
  args->counter = 3;
  return NULL;
}
void* run_write_benchmark_thread(void* void_args){
  struct benchmark_thread_args* args = (struct benchmark_thread_args*) void_args;
  //volatile biguint* arr = args->arr;
  biguint to_push = (struct biguint) {0};
  int err1 = gettimeofday((&args->start), NULL);
  for (long long int i = 0; i < args->iters; i++){
    for (long long int j = 0; j < args->size/sizeof(biguint); j++){
      args->arr[j] = to_push; // push the struct
    }
  }
  int err2 = gettimeofday(&(args->end), NULL);
  args->counter = 2;
  return NULL;
}
void run_write_rand_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size){
  long long iters = total/size;
  pthread_t threads[NUM_THREADS];
  long long l1_size = sysconf(_SC_LEVEL1_DCACHE_SIZE);
  struct benchmark_thread_args thread_args[NUM_THREADS];
  long long int alloc_size = (size/sizeof(biguint)) * sizeof(biguint) / NUM_THREADS;
  iters *= alloc_size/(l1_size/2);
  for (uint64_t i = 0; i < NUM_THREADS; i++) {
    biguint* arr = malloc(alloc_size);
    thread_args[i] = (struct benchmark_thread_args) {iters, alloc_size, i, 0};
    if (arr == NULL) { 
      fprintf(stderr, "failed allocating memory"); exit(EXIT_FAILURE); }
    thread_args[i].arr = arr;
    uint32_t* rand_nums = malloc(l1_size/2);
    uint64_t num_rand_nums = l1_size/2/sizeof(uint32_t);   
    for (long long int i = 0; i < num_rand_nums; i++) {
      uint32_t rand_num = rand() % UINT32_MAX;
      while (arr_in(rand_num, i - 1, rand_nums)){
        rand_num = rand() % UINT32_MAX;
      }
      rand_nums[i] = rand_num;
    }
    thread_args[i].rand_num_arr = rand_nums;
    thread_args[i].rand_num_arr_size = num_rand_nums;
  }

  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_create(&threads[i], NULL, run_write_rand_benchmark_thread, &thread_args[i])){
      fprintf(stderr, "Failed to create thread\n");
      exit(EXIT_FAILURE);
    }
    fprintf(stderr, "thread %ld\n", threads[i]);
  }
  double bandwidth = 0;
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_join(threads[i], NULL)){
      fprintf(stderr, "Failed joining thread\n");
    }
    //fwrite(&(thread_args[i].arr[random() % (alloc_size / sizeof(biguint))]), sizeof(biguint), 1, fnull);
    fwrite(&(thread_args[i].counter), sizeof(uint64_t), 1, fnull);
    free(thread_args[i].arr);
    bandwidth += ((double) (alloc_size * iters)/1024/1024/1024)/(((thread_args[i].end.tv_sec * 1000000 + thread_args[i].end.tv_usec) - (thread_args[i].start.tv_sec * 1000000 + thread_args[i].start.tv_usec))/(double)1000000); 
    printf("size: %lld, thread: %ld, cum_band: %lf\n", thread_args[i].size, threads[i], bandwidth );
  }
  fprintf(fout, "%lld,%d,%lf \n", alloc_size * NUM_THREADS /1024, NUM_THREADS, bandwidth);
}
void run_write_seq_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size){
  long long iters = total/size;
  pthread_t threads[NUM_THREADS];
  struct benchmark_thread_args thread_args[NUM_THREADS];
  long long int alloc_size = (size/sizeof(biguint)) * sizeof(biguint) / NUM_THREADS;
  for (uint64_t i = 0; i < NUM_THREADS; i++) {
    biguint* arr = malloc(alloc_size);
    thread_args[i] = (struct benchmark_thread_args) {iters, alloc_size, i, 0};
    if (arr == NULL) { 
      fprintf(stderr, "failed allocating memory"); exit(EXIT_FAILURE); }
    thread_args[i].arr = arr;
  }

  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_create(&threads[i], NULL, run_write_benchmark_thread, &thread_args[i])){
      fprintf(stderr, "Failed to create thread\n");
      exit(EXIT_FAILURE);
    }
    fprintf(stderr, "thread %ld\n", threads[i]);
  }
  double bandwidth = 0;
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_join(threads[i], NULL)){
      fprintf(stderr, "Failed joining thread\n");
    }
    //fwrite(&(thread_args[i].arr[random() % (alloc_size / sizeof(biguint))]), sizeof(biguint), 1, fnull);
    fwrite(&(thread_args[i].counter), sizeof(uint64_t), 1, fnull);
    free(thread_args[i].arr);
    bandwidth += ((double) (alloc_size * iters)/1024/1024/1024)/(((thread_args[i].end.tv_sec * 1000000 + thread_args[i].end.tv_usec) - (thread_args[i].start.tv_sec * 1000000 + thread_args[i].start.tv_usec))/(double)1000000); 
    printf("size: %lld, thread: %ld, cum_band: %lf\n", thread_args[i].size, threads[i], bandwidth );
  }
  fprintf(fout, "%lld,%d,%lf \n", alloc_size * NUM_THREADS /1024, NUM_THREADS, bandwidth);
}
//void run_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size, enum pattern pat){
//  long long iters = total / size;
//  pthread_t threads[NUM_THREADS];
//  struct benchmark_thread_args thread_args[NUM_THREADS];
//  long long int alloc_size = (size/sizeof(biguint)) * sizeof(biguint) / NUM_THREADS;
//}
void run_write_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size, enum pattern pat){
  if (pat == SEQ_WRITE) { run_write_seq_benchmark(NUM_THREADS, fout, fnull, size); }
  else if (pat == RAND_WRITE) { run_write_rand_benchmark(NUM_THREADS, fout, fnull, size); }
}
void run_read_benchmark(int NUM_THREADS, FILE* fout, FILE* fnull, long long int size, enum pattern pat){
  long long iters = total / size;
  pthread_t threads[NUM_THREADS];
  struct benchmark_thread_args thread_args[NUM_THREADS];
  long long int alloc_size = (size/sizeof(biguint)) * sizeof(biguint) / NUM_THREADS;
  //bool rand_pat = true; //TODO: make it an argument
  for (int i = 0; i < NUM_THREADS; i++) {
    biguint* arr = malloc(alloc_size);
    thread_args[i] = (struct benchmark_thread_args) {iters, alloc_size, 0, 0};
    if (arr == NULL) { fprintf(stderr, "failed allocating memory"); exit(EXIT_FAILURE); }

    for (uint64_t i = 0; i < (alloc_size/sizeof(biguint)); i++){
      arr[i].num = i;
    }

    if (pat == RAND_READ){
      for (long long int i = (alloc_size/sizeof(biguint)) - 1; i > 1; i--){
        // copy line from mem_lat
        long long int pos = rand() % (i - 1);
        biguint temp = arr[i];
        arr[i] = arr[pos];
        arr[pos] = temp;
      }
    } 
    else {
      for (uint64_t i = 0; i < (alloc_size/sizeof(biguint)) - 1; i++){
        arr[i].num = i+1;
      }
      arr[alloc_size/sizeof(biguint) - 1].num = 0;
    }
    thread_args[i].arr = arr;
  }
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_create(&threads[i], NULL, run_read_benchmark_thread, &thread_args[i])){
      fprintf(stderr, "Failed to create thread \n");
      exit(EXIT_FAILURE);
    }
  }
  double bandwidth = 0;
  for (int i = 0; i < NUM_THREADS; i++){
    if (pthread_join(threads[i], NULL)){
      fprintf(stderr, "Failed joining thread\n");
    }
    //fwrite(&(thread_args[i].arr[random() % (alloc_size / sizeof(biguint))]), sizeof(biguint), 1, fnull);
    fwrite(&(thread_args[i].counter), sizeof(uint64_t), 1, fnull);
    free(thread_args[i].arr);
    bandwidth += ((double) (alloc_size * iters)/1024/1024/1024)/(((thread_args[i].end.tv_sec * 1000000 + thread_args[i].end.tv_usec) - (thread_args[i].start.tv_sec * 1000000 + thread_args[i].start.tv_usec))/(double)1000000); 
    printf("size: %lld, thread: %ld, cum_band: %lf\n", thread_args[i].size, threads[i], bandwidth );
  }
  fprintf(fout, "%lld,%d,%lf \n", alloc_size * NUM_THREADS /1024, NUM_THREADS, bandwidth);
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
  if (argc != 7){
    fprintf(stderr, "invalid arguments: must be num threads (0 for max threads), starting size (in bytes) (power of 2), ending size (in bytes) (power of 2), length multipler (power of 2), output file, read pattern\n");
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
  enum pattern pat; 
  if (strcmp(argv[6],"SEQ_READ") == 0) {
    pat = SEQ_READ;
  }
  else if (strcmp(argv[6], "RAND_READ") == 0) {
    pat = RAND_READ; 
  }
  else if (strcmp(argv[6], "SEQ_WRITE") == 0){
    pat = SEQ_WRITE;
  }

  FILE* fout = fopen(argv[5], "a");
  FILE* fnull = fopen("/dev/null", "w");

  fprintf(fout, "working set size (kB), pattern, number of threads, average throughput (GB/s) \n");
  
//  ()(*run_benchmark(int, FILE*, FILE*, long long, enum pattern));
 // if (pat == SEQ_READ || pat == RAND_READ){

  //}
  if (pat == SEQ_READ || pat == RAND_READ){
    if ( START_SIZE == END_SIZE ) {
      run_read_benchmark(NUM_THREADS, fout, fnull, START_SIZE, pat);
      exit(EXIT_SUCCESS);
    }
    long long int sizes_size = log2u(END_SIZE / START_SIZE) + 2 + 9;
    long long int* sizes = malloc(sizes_size * sizeof(long long int));
    sizes[0] = START_SIZE;
    merge_list( sizes_size, sizes, 9, cache_sizes);
    for (int i = 0; sizes[i] < END_SIZE && i < log2u(END_SIZE/ START_SIZE) + 2 + 9; i++)
      run_read_benchmark(NUM_THREADS, fout, fnull, sizes[i], pat);
    run_read_benchmark(NUM_THREADS, fout, fnull, END_SIZE, pat);

    exit(EXIT_SUCCESS);
  } 
  else if (pat == SEQ_WRITE || pat == RAND_WRITE){
    if (START_SIZE == END_SIZE) {
      run_write_benchmark(NUM_THREADS, fout, fnull, START_SIZE, pat);
      exit(EXIT_SUCCESS);
    }
    long long int sizes_size = log2u(END_SIZE / START_SIZE) + 2 + 9;
    long long int* sizes = malloc(sizes_size * sizeof(long long int));
    sizes[0] = START_SIZE;
    merge_list( sizes_size, sizes, 9, cache_sizes);
    for (int i = 0; sizes[i] < END_SIZE && i < log2u(END_SIZE/ START_SIZE) + 2 + 9; i++)
      run_write_benchmark(NUM_THREADS, fout, fnull, sizes[i], pat);
    run_write_benchmark(NUM_THREADS, fout, fnull, END_SIZE, pat);
  }
}
