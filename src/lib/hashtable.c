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

#include "hashtable.h"

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
    unsigned int a_size = 0; /* -Wall */
    
    /* size > goodprimes[-1] */
    if(size > ht_goodprimes[ht_len_gp - 1])
        return NULL;
    
    for(i=0; i < ht_len_gp; i++)
        if(ht_goodprimes[i] > size){
            a_size = ht_goodprimes[i];
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
    h->loadlimit = ht_items_per_place * a_size;
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

struct ht_entry* ht_pop(struct ht_hashtable* h, ht_keytype key){
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
    struct ht_entry* prev = NULL;
    struct ht_entry* e = h->table[idx];
    if(e == NULL)
        return NULL;
    while(!h->eqfn(key, e->key)){
        prev = e;
        e = e->next;
        if(e == NULL)
            return NULL;
    }
    if(prev == NULL){
        h->table[idx] = e->next;
    } else{
        prev->next = e->next;
    }
    return e;
}

unsigned char ht_insert(struct ht_hashtable* h, ht_keytype key,
                        ht_valuetype value){
    struct ht_entry* e = (struct ht_entry*) malloc(sizeof(struct ht_entry));
    if(e == NULL)
        return 0;
    e->key = key;
    e->value = value;
    e->next = NULL;
    if(++(h->entries) > h->loadlimit){
        ht_expand(h);
    }
    unsigned int idx = ht_hash(h->hashfn(key)) % h->length;
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
    struct ht_entry* next;
    struct ht_entry** new_table;

    unsigned int i, idx;
    
    new_table = (struct ht_entry**) calloc(n, sizeof(struct ht_entry*));
    if(new_table != NULL){
        for(i=0; i < h->length; i++){
            e = h->table[i];
            while(e != NULL){
                next = e->next;
                e->next = NULL;
                idx = ht_hash(h->hashfn(e->key)) % n;
                if(new_table[idx] == NULL){
                    new_table[idx] = e;
                } else{
                    struct ht_entry* l;
                    l = new_table[idx];
                    while(l->next != NULL){
                        l = l->next;
                    }
                    l->next = e;
                }
                e = next;
            }
        }
        free(h->table);
        h->table = new_table;
    } else{
        struct ht_entry* prev;
        new_table = (struct ht_entry**) realloc(h->table, n * sizeof(struct entry *));
        if(new_table == NULL)
            return 0;
        h->table = new_table;
        for(i=h->length; i < n; i++)
            h->table[i] = NULL;
        
        for(i=0; i < h->length; i++){
            e = h->table[i];
            prev = NULL;
            while(e != NULL){
                idx = ht_hash(h->hashfn(e->key)) % n;
                next = e->next;
                if(h->table[idx] == NULL){
                    h->table[idx] = e;
                } else{
                    e->next = h->table[idx];
                    h->table[idx] = e;
                }
                if(prev != NULL)
                    prev->next = next;
                prev = e;
                e = next;
            }
        }
    }
    h->length = n;
    h->loadlimit = n * ht_items_per_place;
    return 1; 
}

unsigned char ht_expand(struct ht_hashtable* h){
    if(h->primeidx == (ht_len_gp - 1))
        return 0;
    if(ht_resize(h, ht_goodprimes[++(h->primeidx)])){
        return 1;
    } else{
        h->length = ht_goodprimes[--(h->primeidx)];
        return 0;
    }
}

struct ht_iter* ht_iter_new(struct ht_hashtable* h){
    struct ht_iter* it = (struct ht_iter*) malloc(sizeof(struct ht_iter));
    it->h = h;
    it->i = 0;
    while(it->i < it->h->length && h->table[it->i] == NULL)
        it->i++;
    it->e = h->table[it->i];
    return it;
}

struct ht_entry* ht_iter_next(struct ht_iter* it){
    struct ht_entry* ret;
    ret = it->e;
    if(it->e->next != NULL){
        it->e = it->e->next;
    } else{
        if(++(it->i) >= it->h->length)
            return NULL;
        while(it->i < it->h->length && it->h->table[it->i] == NULL)
            it->i++;
        it->e = it->h->table[it->i];
    }
    return ret;
}
