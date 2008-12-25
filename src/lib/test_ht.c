/* Costumize the hashtable. This has to be done at compile time, and before
#include "hashtable.h"! */

#define ht_keytype unsigned int
#define ht_valuetype unsigned int
#define ht_freevalues 0

#include "hashtable.c"

int main(){
    unsigned int hash(unsigned int key){
        return key;
    }
    
    unsigned char eq(unsigned int one, unsigned int other){
        return one == other;
    }
    /* Testing goes here! */
    struct ht_hashtable* h = ht_new(10, hash, eq);
    unsigned int a;
    unsigned int b;
    
    a = 5;
    b = 10;
    ht_insert(h, a, b);
    printf("10: %u\n", ht_lookup(h, a)->value);
    a = 15;
    b = 12;
    ht_insert(h, a, b);
    printf("12: %u\n", ht_lookup(h, a)->value);
    a = 24;
    b = 82;
    ht_insert(h, a, b);
    printf("82: %u\n", ht_lookup(h, a)->value);
    a = 11;
    b = 14;
    ht_insert(h, a, b);
    printf("14: %u\n", ht_lookup(h, a)->value);
    a = 19;
    b = 6;
    ht_insert(h, a, b);
    printf("6: %u\n", ht_lookup(h, a)->value);
    a = 17;
    b = 155;
    ht_insert(h, a, b);
    printf("155: %u\n", ht_lookup(h, a)->value);
    a = 150;
    b = 125;
    ht_insert(h, a, b);
    printf("125: %u\n", ht_lookup(h, a)->value);
    a = 115;
    b = 122;
    ht_insert(h, a, b);
    printf("122: %u\n", ht_lookup(h, a)->value);
    
    
    ht_expand(h);
    printf("122: %u\n", ht_lookup(h, a)->value);
    printf("155: %u\n", ht_lookup(h, 17)->value);
    return 0;
}
