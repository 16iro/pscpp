// Segment Tree — point update, range query (sum)
struct SegTree {
    int n;
    vector<ll> tree;
    SegTree(int n) : n(n), tree(2 * n, 0) {}

    void update(int i, ll val) {
        for (tree[i += n] = val; i > 1; i >>= 1)
            tree[i >> 1] = tree[i] + tree[i ^ 1];
    }
    ll query(int l, int r) { // [l, r)
        ll res = 0;
        for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += tree[l++];
            if (r & 1) res += tree[--r];
        }
        return res;
    }
};
