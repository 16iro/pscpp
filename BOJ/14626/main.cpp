#include <bits/stdc++.h>
using namespace std;

int rmap[] = {0, 7, 4, 1, 8, 5, 2, 9, 6, 3};

int ctoi(char c) {
    return c - '0';
}

void solve() {
    // input
    string input;
    cin >> input;

    // calculate
    int result = 0;
    int c_idx = -1;
    int sum = 0;
    for (int idx = 0; idx < 12; idx++) {
        bool corrupt = input[idx] == '*';
        if (corrupt) {
            c_idx = idx;
        } else {
            sum += ctoi(input[idx]) * (idx % 2 == 0 ? 1 : 3);
            sum %= 10;
        }
    }
    int m = ctoi(input[12]);
    bool is_c_even = c_idx % 2 == 0;
    if (is_c_even) {
        result = (10 - (m + sum) % 10) % 10;
    } else {
        int modR = (10 - (m + sum) % 10) % 10;
        result = rmap[modR];
    }
    cout << result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
