#include <bits/stdc++.h>
using namespace std;

void solve() {
    int N;
    cin >> N;
    for (int n = 0; n < N; n++) {
        string pw;
        cin >> pw;
        cout << (pw.size() >= 6 && pw.size() <= 9 ? "yes" : "no") << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
