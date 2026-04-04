#include <bits/stdc++.h>
using namespace std;

vector<pair<string, int>> arr;

void solve() {
    int TC;
    cin >> TC;
    for (int tc = 0; tc < TC; tc++) {
        int N;
        cin >> N;
        arr.clear();
        for (int n = 0; n < N; n++) {
            string name, group;
            cin >> name >> group;
            auto it = find_if(arr.begin(), arr.end(),
                              [&](const pair<string, int>& p) -> bool { return p.first == group; });
            if (it != arr.end()) {
                it->second += 1;
            } else {
                arr.push_back(pair(group, 1));
            }
        }
        int result = 1;
        for (int idx = 0; idx < (int)arr.size(); idx++) {
            result *= (arr[idx].second + 1);
        }
        cout << result - 1 << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
