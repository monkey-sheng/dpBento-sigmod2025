#include <cstdint>
#include <cstdio>
#include <experimental/random>
#include <cstdlib>
#include <iostream>
#include <iterator>
#include <sys/times.h>
#include <sys/time.h>
long long int total = (long long)1024 * 1024 * 1024 * 128 * 2;

//long long int array_size =  80 * 1024 / 4;
//long long int iters = 1024  * 10 ;
struct biguint{
  uint64_t num;
  uint64_t padding[7];
};
int main(){
  FILE* fnull = fopen("/dev/null", "w");
  struct timeval seed;
  long long int size = 1024;
  biguint* arr = (biguint*) malloc(sizeof(uint64_t)*8);
  for (long long int size = 1024; size < 1024 * 1024 * 64; size *= 2){
    long long iters = total / size;

    arr = (biguint*) realloc(arr, size);
    for (uint64_t i = 0; i < size / sizeof(biguint); i++){
      arr[i].num = i;
    }
    //gettimeofday(&seed, NULL);
    //std::srand(seed.tv_usec);
    for (long long int i = (size/sizeof(biguint)) - 1; i > 1; i--){
      std::experimental::reseed();
      long long int pos = std::experimental::randint((long long int) 0, i - 1);
      //long long int pos = random() % (i - 1);
      //long long int pos = std::rand() % (i - 1);
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
    uint64_t tmp = k;
    fwrite(&tmp, sizeof(uint64_t), 1, fnull);
    if (err1 || err2) { printf("error getting time\n");}
    printf("%lld kB, %lf nanoseconds per op \n", size/1024, ((end.tv_sec * 1000000 + end.tv_usec) - (start.tv_sec * 1000000 + start.tv_usec))/((double)total/sizeof(biguint))*1000);
  }

}
