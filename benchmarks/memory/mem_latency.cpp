#include <cstdint>
#include <cstdio>
#include <experimental/random>
#include <cstdlib>
#include <iostream>
#include <iterator>
#include <sys/times.h>
#include <sys/time.h>
#include <unistd.h>
#include <string.h>
long long int total = (long long)1024 * 1024 * 1024;

struct biguint{
  uint64_t num;
  uint64_t padding[7];
};

biguint* run_benchmark(FILE* fout, FILE* fnull, long long int size, double adjustment){
  long long iters = total / size;
  biguint* arr = (biguint*) malloc(size);
  for (uint64_t i = 0; i < size / sizeof(biguint); i++){
    arr[i].num = i;
  }
  for (long long int i = (size/sizeof(biguint)) - 1; i > 1; i--){
    std::experimental::reseed();
    long long int pos = std::experimental::randint((long long int) 0, i - 1);
    biguint temp = arr[i];
    arr[i] = arr[pos];
    arr[pos] = temp;
  }
  uint64_t k = 0;;
  struct timeval start;
  struct timeval end;
  int err1 = gettimeofday(&start, NULL);
  //actual benchmark here
  for (long long int i = 0; (i < iters); i++){
    for (long long int j = 0; j < size/sizeof(biguint); j++){
      k = arr[k].num;
    }
  }
  int err2 = gettimeofday(&end, NULL);
  fwrite(&arr[k], sizeof(uint64_t), 8, fnull);
  if (err1 || err2) { printf("error getting time\n");}
  free(arr);
  fprintf(fout, "%lld,%lf\n", size/1024, (((end.tv_sec * 1000000 + end.tv_usec) - (start.tv_sec * 1000000 + start.tv_usec))/((double)total/sizeof(biguint))*1000) - adjustment);
  return arr; 
}

double get_adjustment(FILE* fnull){
  long long iters = total/sizeof(uint64_t);
  uint64_t* arr = (uint64_t*) malloc(3 * sizeof(uint64_t));
  for (uint64_t i = 0; i < 3; i++) { arr[i] = i; }
  if (random() % 2) { arr[0] = 2; arr[1] = 0; arr[2] = 1;}
  else { arr[0] = 1; arr[1] = 2; arr[2] = 0; }
  uint64_t k = 0;
  struct timeval start;
  struct timeval end;
  int err1 = gettimeofday(&start, NULL);
  //actual benchmark here
  for (long long int i = 0; (i < iters); i++){
      k = arr[k];
  }
  int err2 = gettimeofday(&end, NULL);
  if (err1 || err2) { return -1; }
  fprintf(stderr, "%lf\n", ((end.tv_sec * 1000000 + end.tv_usec) - (start.tv_sec * 1000000 + start.tv_usec))/((double)total/sizeof(uint64_t))*1000 / 3);
  fprintf(fnull, "%ld", k);
  return ((end.tv_sec * 1000000 + end.tv_usec) - (start.tv_sec * 1000000 + start.tv_usec))/((double)total/sizeof(uint64_t))*1000 / 3;
}
int main(int argc, char** argv){
  if (argc != 5){
    fprintf(stderr, "invalid arguments: must be starting size (power of 2), end size (in bytes) (power of 2), length multiplier (power of 2), output file\n");
    exit(EXIT_FAILURE);
  }
  char** temp = NULL;
  long long START_SIZE;
  if (strcmp(argv[1], "L1_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL1_DCACHE_SIZE); }
  else if (strcmp(argv[1], "L2_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL2_CACHE_SIZE); }
  else if (strcmp(argv[1], "L3_cache") == 0) { START_SIZE = sysconf(_SC_LEVEL3_CACHE_SIZE); }
  else {START_SIZE = std::strtoll(argv[1], temp, 10); }
  long long END_SIZE; 
  if (strcmp(argv[2], "L1_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL1_DCACHE_SIZE); }
  else if (strcmp(argv[2], "L2_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL2_CACHE_SIZE); }
  else if (strcmp(argv[2], "L3_cache") == 0) { END_SIZE = sysconf(_SC_LEVEL3_CACHE_SIZE); }
  else { END_SIZE = std::strtoll(argv[2], temp, 10); }
  total = std::strtoll(argv[3], temp, 10) * total;
  long long l1_size = sysconf(_SC_LEVEL1_DCACHE_SIZE);
  long long l2_size = sysconf(_SC_LEVEL2_CACHE_SIZE);
  long long l3_size = sysconf(_SC_LEVEL3_CACHE_SIZE);
  FILE* fout = fopen(argv[4], "w");
  FILE* fnull = fopen("/dev/null", "w");
  fprintf(fout, "working set size (kB),nanoseconds/ops\n");
  double adjustment = get_adjustment(fnull);
  if ( START_SIZE == END_SIZE ){
    run_benchmark(fout, fnull, START_SIZE, adjustment);
    exit(EXIT_SUCCESS);
  }
  run_benchmark(fout, fnull, START_SIZE, adjustment);
  for (long long int size = 1024; size < END_SIZE; size *= 2){
    if (size <= START_SIZE) { continue; }
    run_benchmark(fout, fnull, size, adjustment);
    if (size < l1_size && size * 2 > l1_size){
      run_benchmark(fout, fnull, l1_size, adjustment);
    }
    if (size < l2_size && size * 2 > l2_size){
      run_benchmark(fout, fnull, l2_size, adjustment);
    }
    if (l3_size != -1 && l3_size != 0 && size < l3_size && size * 2 > l3_size) { 
      run_benchmark(fout, fnull, l3_size, adjustment);
    }
    run_benchmark(fout, fnull, END_SIZE, adjustment);
  }
  exit(EXIT_SUCCESS);
}
