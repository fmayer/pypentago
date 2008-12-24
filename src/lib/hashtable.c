#include <stdlib.h>
#include <stdio.h>
#include "hashtable.h"

#ifndef true
#define true 1
#define false 0
#endif


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
                                    unsigned int (*hashf) (void*),
                                    unsigned char (*eqf) (void*, void*)){
    unsigned int i;
    unsigned int a_size;
    
    /* NULL entry. By default, the hashtable is filled with it. */
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
    for(i=0; i < sizeof(struct ht_entry*) * size; i++)
        h->table[i] = n_entry;
    
    return h;
}

struct ht_entry* ht_lookup(struct ht_hashtable* h, void* key){
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
    struct ht_entry* e = h->table[idx];
    while(!h->eqfn(key, e->key)){
        e = e->next;
        if(e == NULL)
            return NULL;
    }
    return e;
}

unsigned char ht_insert(struct ht_hashtable* h, void* key, void* value){
    unsigned int hash = ht_hash(h->hashfn(key));
    unsigned int idx = hash % h->length;
    struct ht_entry* e = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    if(e == NULL)
        return false;
    e->key = key;
    e->value = value;
    e->hash = hash;
    e->next = NULL;
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
    return true;
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

void ht_expand(struct ht_hashtable* h){
    struct ht_entry** new_table;
    unsigned int n = goodprimes[++(h->primeidx)];
    unsigned int i;
    
    struct ht_entry* n_entry = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    if(n_entry == NULL)
        return NULL;
    n_entry->key = NULL;
    n_entry->value = NULL;
    
    new_table = (struct ht_entry**) malloc(sizeof(struct ht_entry*) * n);
    if(new_table == NULL)
        return NULL;
    for(i=0; i < sizeof(struct ht_entry*) * n; i++)
        new_table[i] = n_entry;
    
    for(i=0; i < h->length; i++){
        
    }
        
    
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
    unsigned int a = 5;
    unsigned int b = 10;
    ht_insert(h, &a, &b);
    printf("%u\n", *((unsigned int*) ht_lookup(h, &a)->key));
    
    return 0;
}