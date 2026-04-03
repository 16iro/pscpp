#include <bits/stdc++.h>
using namespace std;

// key=>value
vector<pair<int, string>> kv;
// value=>key
vector<pair<string, int>> vk;

bool compare(pair<string, int> p1, pair<string, int> p2) {
    return p1.first.compare(p2.first) <= 0;
}
bool isNumber(string input) {
    return input[0] - '0' >= 0 && input[0] - '0' <= 9;
}

int bsearch(string input) {
    int min = 0;
    int max = kv.size() - 1;
    while (min <= max) {
        int mid = (min + max) / 2;
        int cmp_result = input.compare(vk[mid].first);
        if (cmp_result == 0) {
            return vk[mid].second;
        } else if (cmp_result < 0) {
            max = mid - 1;
        } else {
            min = mid + 1;
        }
    }
    return -1;
}

void solve() {
    int N, M;
    cin >> N >> M;
    for (int n = 0; n < N; n++) {
        string pokemon;
        cin >> pokemon;
        kv.push_back(pair(n + 1, pokemon));
        vk.push_back(pair(pokemon, n + 1));
    }
    sort(vk.begin(), vk.end(), compare);
    for (int m = 0; m < M; m++) {
        string input;
        cin >> input;
        if (isNumber(input)) {
            cout << kv[stoi(input) - 1].second << "\n";
        } else {
            cout << bsearch(input) << "\n";
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
