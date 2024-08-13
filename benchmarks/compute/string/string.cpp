#include <fstream>
#include <iostream>
#include <string>
#include <chrono>
#include <string_view>

using std::string;
using std::chrono::high_resolution_clock;


#define N_LINES_PER_BLOCK (50000000)

int main() {
    std::ifstream *file;
    std::ifstream p_type("/home/jason/DPU-bench/benchmarks/compute/string/p_type.txt");
    std::ifstream c_phone("/home/jason/DPU-bench/benchmarks/compute/string/c_phone.txt");
    std::ifstream p_container("/home/jason/DPU-bench/benchmarks/compute/string/p_container.txt");
    // create a new array of strings of size n
    string* str_block = new string[N_LINES_PER_BLOCK];

    // the strings to match, extracted from tpc-h
    string p_type_like_COPPER = "COPPER";  // reverse find
    string p_type_not_like_ECONOMY_POLISHED = "ECONOMY POLISHED";  // in-order find
    string p_type_eq_ECONOMY_ANODIZED_STEEL = "ECONOMY ANODIZED STEEL";  // exact match
    string c_phone_substring[] = {"31", "19", "22", "25", "20", "28", "24"};
    string p_container_in[] = {"MED BAG", "MED BOX", "MED PKG", "MED PACK"};  // exact match

    
    std::chrono::time_point<high_resolution_clock> start_time, end_time;

    if (!(p_type.is_open())) {
        std::cout << "Unable to open p_type" << std::endl;
        return -1;
    }

    bool do_loop = true;
    int total_lines = 0;
    size_t i, j, k;

    uint like_copper_matches = 0;
    uint not_like_economy_polished_matches = 0;
    uint eq_economy_anodized_steel_matches = 0;
    uint phone_substring_matches = 0;
    uint p_container_in_matches = 0;
    // uint match_string_size;

    std::chrono::nanoseconds like_copper_duration{0};
    std::chrono::nanoseconds not_like_economy_polished_duration{0};
    std::chrono::nanoseconds eq_economy_anodized_steel_duration{0};
    std::chrono::nanoseconds phone_substring_duration{0};
    std::chrono::nanoseconds p_container_in_duration{0};

    // while loop for p_type
    file = &p_type;
    while (do_loop) {
        for (i = 0; i < N_LINES_PER_BLOCK; i++) {
            if (!std::getline(*file, str_block[i])) {
                do_loop = false;
                break; // Reached end of file before reading all lines
            }
        }
        
        // match like copper
        start_time = high_resolution_clock::now();
        for (j = 0; j < i; j++) {
            if (str_block[j].ends_with(p_type_like_COPPER)) {
                like_copper_matches++;
            }
        }
        end_time = high_resolution_clock::now();
        like_copper_duration += std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);

        // match not like economy polished
        start_time = high_resolution_clock::now();
        for (j = 0; j < i; j++) {
            if (!str_block[j].starts_with(p_type_not_like_ECONOMY_POLISHED)) {
                not_like_economy_polished_matches++;
            }
        }
        end_time = high_resolution_clock::now();
        not_like_economy_polished_duration += std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);

        // match eq economy anodized steel
        start_time = high_resolution_clock::now();
        for (j = 0; j < i; j++) {
            if (str_block[j] == p_type_eq_ECONOMY_ANODIZED_STEEL) {
                eq_economy_anodized_steel_matches++;
            }
        }
    
        end_time = high_resolution_clock::now();
        eq_economy_anodized_steel_duration += std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
    }

    // while loop for c_phone
    file = &c_phone;
    do_loop = true;
    while (do_loop) {
        for (i = 0; i < N_LINES_PER_BLOCK; i++) {
            if (!std::getline(*file, str_block[i])) {
                do_loop = false;
                break; // Reached end of file before reading all lines
            }
        }
        start_time = high_resolution_clock::now();
        
        // match phone substring
        bool found = false;
        start_time = high_resolution_clock::now();
        for (j = 0; j < i; j++) {
            for (k = 0; k < 7; k++) {
                if (str_block[j].starts_with(c_phone_substring[k])) {
                    phone_substring_matches++;
                    found = true;
                    break;
                }
            }
        }
        end_time = high_resolution_clock::now();
        phone_substring_duration += std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
    }
    
    // while loop for p_container
    file = &p_container;
    do_loop = true;
    while (do_loop) {
        for (i = 0; i < N_LINES_PER_BLOCK; i++) {
            if (!std::getline(*file, str_block[i])) {
                do_loop = false;
                break; // Reached end of file before reading all lines
            }
        }
        start_time = high_resolution_clock::now();

        // match in p_container
        bool found = false;
        start_time = high_resolution_clock::now();
        for (j = 0; j < i; j++) {
            for (k = 0; k < 4; k++) {
                if (str_block[j] == p_container_in[k]) {
                    p_container_in_matches++;
                    found = true;
                    break;
                }
            }
        }
        end_time = high_resolution_clock::now();
        p_container_in_duration += std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
    }
    
    printf("Like COPPER matches: %d\n", like_copper_matches);
    printf("Not like ECONOMY POLISHED matches: %d\n", not_like_economy_polished_matches);
    printf("Equal to ECONOMY ANODIZED STEEL matches: %d\n", eq_economy_anodized_steel_matches);
    printf("Phone substring matches: %d\n", phone_substring_matches);
    printf("P_CONTAINER matches: %d\n", p_container_in_matches);

    printf("Like COPPER duration: %ld\n", like_copper_duration.count() / 1000);
    printf("Not like ECONOMY POLISHED duration: %ld\n", not_like_economy_polished_duration.count() / 1000);
    printf("Equal to ECONOMY ANODIZED STEEL duration: %ld\n", eq_economy_anodized_steel_duration.count() / 1000);
    printf("Phone substring duration: %ld\n", phone_substring_duration.count() / 1000);
    printf("P_CONTAINER duration: %ld\n", p_container_in_duration.count() / 1000);

    p_type.close();
    c_phone.close();
    p_container.close();
    // printf("Total lines read: %d\n", total_lines);
    return 0;
}