#include <bits/stdc++.h>
using namespace std;

int arr[1001];
void solve() {
    int N;
    cin >> N;
    for (int a = 0; a <= N; a++) {
        arr[a] = a < 2 ? 1 : arr[a - 1] + arr[a - 2];
    }
    cout << arr[N];
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t = 1;
    // cin >> t;       // 멀티 테스트케이스일 경우 주석 해제
    while (t--)
        solve();

    return 0;
}
