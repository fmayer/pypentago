/* Costumize the hashtable. This has to be done at compile time. */
#define ht_keytype unsigned int
#define ht_valuetype unsigned int
#define ht_freevalues 0

/* Yes, this is supposed to be hashtable.c. We have to statically link as
 * the source-code changes depending on our choices for ht_keytype,
 * ht_valuetype and ht_freevalues. */
#include "hashtable.c"

#define lookback 159
#define testsize 1000000

int main(){
    unsigned int hash(unsigned int key){
        return key;
    }
    
    unsigned char eq(unsigned int one, unsigned int other){
        return one == other;
    }
    /* Testing goes here! */
    struct ht_hashtable* h = ht_new(10, hash, eq);
    unsigned int a, r;
    r = 0;
    struct ht_entry* b;
    
    for(a=0; a < testsize; a++){
        ht_insert(h, a, a+21);
        b = ht_lookup(h, a);
        if(b == NULL){
            printf("%u != NULL\n", a+21);
            r = 1;
        } else if(a+21 != b->value){
            printf("%u != %u\n", a+21, b->value);
            r = 1;
        }
        if(a > lookback){
            b = ht_lookup(h, a-lookback);
            if(b == NULL){
                printf("%u != NULL\n", a-lookback+21);
                r = 1;
            } else if(a-lookback+21 != b->value){
                printf("%u != %u\n", a-lookback+21, b->value);
                r = 1;
            }
        }
    }
    a = 0;
    struct ht_iter* it = ht_iter_new(h);
    struct ht_entry* e;
    while((e = ht_iter_next(it)) != NULL){
        a++;
    }
    if(a != (testsize - 1))
        printf("Iter too short!\n");
    return r;
}
