
#ifndef keytype
#define keytype void*
#define valuetype void*
#endif

static const unsigned int goodprimes[] = {
53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613,
393241, 786433, 1572869, 3145739, 6291469, 12582917, 25165843, 50331653,
100663319, 201326611, 402653189, 805306457, 1610612741};

const unsigned int len_goodprimes = sizeof(goodprimes)/sizeof(goodprimes[0]);

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
    unsigned int (*hashfn) (keytype k);
    /* Function to compare keys. */
    unsigned char (*eqfn) (keytype k1, keytype k2);
    struct ht_entry* n_entry;
};

struct ht_entry
{
    valuetype value;
    keytype key;
    unsigned int hash;
    struct ht_entry* next;
};

struct ht_hashtable* ht_new_hashtable(unsigned int size,
                                    unsigned int (*hashf) (keytype),
                                    unsigned char (*eqf) (keytype, keytype));
struct ht_entry* ht_lookup(struct ht_hashtable* h, keytype key);
unsigned char ht_insert(struct ht_hashtable* h, keytype key, valuetype value);
void ht_free_hashtable(struct ht_hashtable* h);
unsigned int ht_hash(unsigned int i);
unsigned char ht_expand(struct ht_hashtable* h);
