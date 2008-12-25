#include <stdlib.h>
#include <stdio.h>
#include "hashtable.h"

const float items_per_place = 65. / 100;

unsigned int ht_hash(unsigned int i){
    /* Aim to protect against poor hash functions by adding logic here
     * - logic taken from java 1.4 hashtable source */
    i += ~(i << 9);
    i ^=  ((i >> 14) | (i << 18)); /* >>> */
    i +=  (i << 4);
    i ^=  ((i >> 10) | (i << 22)); /* >>> */
    return i;
}

struct ht_hashtable* ht_new_hashtable(unsigned int size,
                                    unsigned int (*hashf) (keytype),
                                    unsigned char (*eqf) (keytype, keytype)){
    unsigned int i;
    unsigned int a_size;
    
    struct ht_entry* n_entry = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    n_entry->key = NULL;
    n_entry->value = NULL;
    
    /* size > goodprimes[-1] */
    if(size > 161061274)
        return NULL;
    
    for(i=0; i < len_goodprimes; i++)
        if(goodprimes[i] > size){
            a_size = goodprimes[i];
            break;
        }
    
    struct ht_hashtable* h = (struct ht_hashtable*) malloc(sizeof(struct ht_hashtable));
    if(h == NULL)
        return NULL;
    h->table = (struct ht_entry**) malloc(sizeof(struct ht_entry*) * a_size);
    h->length = a_size;
    h->primeidx = i;
    h->hashfn = hashf;
    h->eqfn = eqf;
    h->loadlimit = items_per_place * a_size;
    h->entries = 0;
    h->n_entry = n_entry;
    for(i=0; i < sizeof(struct ht_entry*) * a_size; i++)
        h->table[i] = n_entry;
    
    return h;
}

struct ht_entry* ht_lookup(struct ht_hashtable* h, keytype key){
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
    struct ht_entry* e = h->table[idx];
    if(e->key == NULL)
        return NULL;
    while(!h->eqfn(key, e->key)){
        e = e->next;
        if(e->key == NULL)
            return NULL;
    }
    return e;
}

unsigned char ht_insert(struct ht_hashtable* h, keytype key, valuetype value){
    unsigned int hash = ht_hash(h->hashfn(key));
    unsigned int idx = hash % h->length;
    struct ht_entry* e = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    if(e == NULL)
        return 0;
    e->key = key;
    e->value = value;
    e->hash = hash;
    e->next = NULL;
    if(++(h->entries) > h->loadlimit){
        ht_expand(h);
    }
    if((h->table[idx])->key == NULL){
        h->table[idx] = e;
        h->entries++;
    } else{
        struct ht_entry* l;
        l = h->table[idx];
        while(l->next != NULL)
            l = l->next;
        l->next = e;
    }
    return 1;
}

void ht_free_hashtable(struct ht_hashtable* h){
    unsigned int i;
    for(i=0; i < sizeof(struct ht_entry*) * h->length; i++){
        free((h->table[i])->key);
        free((h->table[i])->value);
        free(h->table[i]);
    }
    free(h->table);
    free(h);
}

unsigned char ht_expand(struct ht_hashtable* h){
    struct ht_entry* e;
    struct ht_entry** new_table;
    if(h->primeidx == (len_goodprimes - 1))
        return 0;
    unsigned int n = goodprimes[++(h->primeidx)];
    unsigned int i, idx;
    
    new_table = (struct ht_entry**) malloc(sizeof(struct ht_entry*) * n);
    if(new_table == NULL)
        return 0;
    for(i=0; i < sizeof(struct ht_entry*) * n; i++)
        new_table[i] = h->n_entry;
    
    for(i=0; i < h->length; i++){
        e = h->table[i];
        while(e != NULL && e->key != NULL){
            idx = e->hash % n;
            if(new_table[idx] == NULL)
                new_table[idx] = e;
            else{
                struct ht_entry* l;
                l = new_table[idx];
                while(l->next != NULL)
                    l = l->next;
                l->next = e;
            }
            e = e->next;
        }
    }
    free(h->table);
    h->table = new_table;
    return 1;
}
int main(){
    unsigned int hash(void* key){
        return *((unsigned int*) key);
    }
    
    unsigned char eq(void* one, void* other){
        return *((unsigned int*) one) == *((unsigned int*) other);
    }
    /* Testing goes here! */
    struct ht_hashtable* h = ht_new_hashtable(10, hash, eq);
    unsigned int* a = malloc(sizeof(int));
    unsigned int* b = malloc(sizeof(int));
    
    *a = 5;
    *b = 10;
    ht_insert(h, a, b);
    printf("10: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 15;
    *b = 12;
    ht_insert(h, a, b);
    printf("12: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 24;
    *b = 82;
    ht_insert(h, a, b);
    printf("82: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 11;
    *b = 14;
    ht_insert(h, a, b);
    printf("14: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 19;
    *b = 6;
    ht_insert(h, a, b);
    printf("6: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 17;
    *b = 155;
    ht_insert(h, a, b);
    printf("155: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 150;
    *b = 125;
    ht_insert(h, a, b);
    printf("125: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    *a = 115;
    *b = 122;
    ht_insert(h, a, b);
    printf("122: %u\n", *((unsigned int*) ht_lookup(h, a)->value));
    
    return 0;
}
