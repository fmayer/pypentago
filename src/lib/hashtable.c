/* pypentago - a board game
Copyright (C) 2008 Florian Mayer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. */

/* TODO: dynamic type of hash? */

#include <stdlib.h>
#include <stdio.h>

/* Costumize the hashtable. This has to be done at compile time, and before
#include "hashtable.h"! */
#define ht_keytype unsigned int
#define ht_valuetype unsigned int
#define ht_freevalues 0

#include "hashtable.h"

/* How many items come to one allocated slot for a ht_entry.
Usually this should be lower than zero. */
const float items_per_place = 65. / 100;

unsigned int ht_hash(unsigned int i){
    /* Protect against poor hashing functions. */
    i += ~(i << 9);
    i ^=  ((i >> 14) | (i << 18)); /* >>> */
    i +=  (i << 4);
    return i ^ ((i >> 10) | (i << 22)); /* >>> */
}

struct ht_hashtable* ht_new(unsigned int size,
                             unsigned int (*hashf) (ht_keytype),
                             unsigned char (*eqf) (ht_keytype, ht_keytype)){
    unsigned int i;
    unsigned int a_size;
    
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
    h->table = (struct ht_entry**) calloc(a_size, sizeof(struct ht_entry*));
    if(h->table == NULL){
        free(h);
        return NULL;
    }
    h->length = a_size;
    h->primeidx = i;
    h->hashfn = hashf;
    h->eqfn = eqf;
    h->loadlimit = items_per_place * a_size;
    h->entries = 0;
    
    return h;
}

struct ht_entry* ht_lookup(struct ht_hashtable* h, ht_keytype key){
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
    struct ht_entry* e = h->table[idx];
    if(e == NULL)
        return NULL;
    while(!h->eqfn(key, e->key)){
        e = e->next;
        if(e == NULL)
            return NULL;
    }
    return e;
}

unsigned char ht_insert(struct ht_hashtable* h, ht_keytype key,
                          ht_valuetype value){
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
    struct ht_entry* e = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    if(e == NULL)
        return 0;
    e->key = key;
    e->value = value;
    e->next = NULL;
    if(++(h->entries) > h->loadlimit){
        ht_expand(h);
    }
    if((h->table[idx]) == NULL){
        h->table[idx] = e;
    } else{
        struct ht_entry* l;
        l = h->table[idx];
        while(l->next != NULL)
            l = l->next;
        l->next = e;
    }
    return 1;
}

void ht_free(struct ht_hashtable* h){
    unsigned int i;
    for(i=0; i < sizeof(struct ht_entry*) * h->length; i++){
        #if ht_freevalues
            free((h->table[i])->key);
            free((h->table[i])->value);
        #endif
        free(h->table[i]);
    }
    free(h->table);
    free(h);
}

unsigned char ht_resize(struct ht_hashtable* h, unsigned int n){
    struct ht_entry* e;
    struct ht_entry** new_table;

    unsigned int i, idx;
    
    new_table = (struct ht_entry**) calloc(n, sizeof(struct ht_entry*));
    if(new_table == NULL)
        return 0;
    
    for(i=0; i < h->length; i++){
        e = h->table[i];
        while(e != NULL){
            idx = ht_hash(h->hashfn(e->key)) % n;
            if(new_table[idx] == NULL){
                new_table[idx] = e;
            } else{
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
    h->length = n;
    h->loadlimit = n * items_per_place;
    return 1;    
    
}

unsigned char ht_expand(struct ht_hashtable* h){
    if(h->primeidx == (len_goodprimes - 1))
        return 0;
    return ht_resize(h, goodprimes[++(h->primeidx)]);
}
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
    return 0;
}
