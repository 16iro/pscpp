#include <bits/stdc++.h>
using namespace std;

vector<pair<string, string>> arr;

bool compare(pair<string, string> a, pair<string, string> b) {
    return a.first.compare(b.first) <= 0;
}

string search(string str) {
    int min = 0;
    int max = arr.size() - 1;
    while (min <= max) {
        int mid = (min + max) / 2;
        int compare = str.compare(arr[mid].first);
        if (compare == 0) {
            return arr[mid].second;
        } else if (compare < 0) {
            max = mid - 1;
        } else {
            min = mid + 1;
        }
    }
    return "";
}

void solve() {
    int N, M;
    cin >> N >> M;
    for (int n = 0; n < N; n++) {
        string k, v;
        cin >> k >> v;
        arr.push_back(pair(k, v));
    }
    sort(arr.begin(), arr.end(), compare);
    for (int m = 0; m < M; m++) {
        string k;
        cin >> k;
        cout << search(k) << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
