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

#ifndef ht_keytype
    #define ht_keytype void*
#endif
#ifndef ht_valuetype
    #define ht_valuetype void*
#endif

#ifndef ht_freevalues
    #define ht_freevalues 1
#endif

#ifndef ht_items_per_place
    #define ht_items_per_place (65. / 100)
#endif

static const unsigned int ht_goodprimes[] = {
53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613,
393241, 786433, 1572869, 3145739, 6291469, 12582917, 25165843, 50331653,
100663319, 201326611, 402653189, 805306457, 1610612741};

const unsigned int ht_len_gp = sizeof(ht_goodprimes)/sizeof(ht_goodprimes[0]);

struct ht_hashtable
{
    /* Items of memory allocated for hashtable. */
    unsigned int length;
    /* Index of the length in goodprimes array. */
    unsigned int primeidx;
    /* Maximum items in hashtable before expand. */
    unsigned int loadlimit;
    /* Amount of items in hashtable. */
    unsigned int entries;
    /* The actual hashtable. */
    struct ht_entry** table;
    /* Function to get hash of the keys. */
    unsigned int (*hashfn) (ht_keytype);
    /* Function to compare keys. */
    unsigned char (*eqfn) (ht_keytype, ht_keytype);
};

struct ht_entry
{
    ht_valuetype value;
    ht_keytype key;
    struct ht_entry* next;
};

struct ht_hashtable* ht_new(unsigned int size,
                            unsigned int (*hashf) (ht_keytype),
                            unsigned char (*eqf) (ht_keytype, ht_keytype));
struct ht_entry* ht_lookup(struct ht_hashtable* h, ht_keytype key);
unsigned char ht_insert(struct ht_hashtable* h, ht_keytype key, ht_valuetype value);
void ht_free(struct ht_hashtable* h);
unsigned int ht_hash(unsigned int i);
unsigned char ht_expand(struct ht_hashtable* h);
unsigned char ht_resize(struct ht_hashtable* h, unsigned int n);
