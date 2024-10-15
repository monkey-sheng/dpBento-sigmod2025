#include <stdint.h>
#include <sys/time.h>
#include <sys/times.h>
#include <stdbool.h>
enum pattern {
  RAND_READ,
  SEQ_READ,
  RAND_WRITE, 
  SEQ_WRITE,
};

struct biguint{
  uint64_t num;
  uint64_t paddng[7];
} typedef biguint;

struct benchmark_thread_args {
  long long int iters;
  long long int size;
  struct timeval start;
  struct timeval end;
  biguint* arr;
  uint32_t* rand_num_arr;
  uint64_t rand_num_arr_size;
};
int get_num_cpu(); // NOTE not really needed rn

void apply_satollos(uint64_t size, biguint arr[size]);
void sort_arr(uint64_t size, uint64_t arr[size]);
long long int poweroftwo(long long int exp);
long long int log2u(long long int num);
void merge_list(long long int pow2_size, long long pow2[pow2_size], long long int merge_size, unsigned long merge_lst[merge_size]);
bool arr_in(uint32_t num, int64_t num_elems, uint32_t elems[num_elems]);
