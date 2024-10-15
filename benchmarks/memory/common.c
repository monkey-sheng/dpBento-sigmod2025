#include "common.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

void apply_satollos(uint64_t size, biguint arr[size]) {
  for (uint64_t i = size - 1; i > 1; i--) {
    uint64_t pos = rand() % (i - 1);
    biguint temp = arr[i];
    arr[i] = arr[pos];
    arr[pos] = temp;
  }
}

void sort_arr(uint64_t size, uint64_t arr[size]){
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
long long int poweroftwo(long long int exp){
  if (exp == 0) { return 1; }
  long long int num = 2;
  while (exp - 1 > 0){
    num *= 2;
    exp--;
  }
  return num;
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
bool arr_in(uint32_t num, int64_t num_elems, uint32_t *elems){
  for (int i = 0; i < num_elems; i++){
    if (elems[i] == num){
      return true;
    }
  }
  return false;
}
