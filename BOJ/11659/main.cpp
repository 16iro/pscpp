#include <bits/stdc++.h>
using namespace std;

int sum[100001];

void solve() {
    int N, M;
    cin >> N >> M;
    for (int n = 0; n < N; n++) {
        int num = 0;
        cin >> num;
        sum[n] += num + (n > 0 ? sum[n - 1] : 0);
    }
    for (int m = 0; m < M; m++) {
        int i, j;
        cin >> i >> j;
        i--;
        j--;
        cout << (sum[j] - (i > 0 ? sum[i - 1] : 0)) << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
