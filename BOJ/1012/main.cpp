#include <bits/stdc++.h>
using namespace std;

// bfs
int arr[50][50];  // M=>N
vector<pair<int, int>> dir = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

void BFS(pair<int, int> rootpos, int count) {
    queue<pair<int, int>> q;
    q.push(rootpos);
    while (!q.empty()) {
        pair<int, int> pos = q.front();
        q.pop();
        arr[pos.first][pos.second] = count;
        for (int d = 0; d < (int)dir.size(); d++) {
            int nx = clamp(pos.first + dir[d].first, 0, 49);
            int ny = clamp(pos.second + dir[d].second, 0, 49);
            if (arr[nx][ny] == -1) {
                arr[nx][ny] = -2;
                q.push(pair(nx, ny));
            }
        }
    }
}

void solve() {
    int T, N, M, K;
    cin >> T;
    for (int t = 0; t < T; t++) {
        // init
        memset(arr, 0, sizeof(arr));
        cin >> M >> N >> K;
        for (int k = 0; k < K; k++) {
            int x, y;
            cin >> x >> y;
            arr[x][y] = -1;
        }

        int count = 0;
        for (int m = 0; m < M; m++) {
            for (int n = 0; n < N; n++) {
                if (arr[m][n] >= 0) {
                    continue;
                } else {
                    BFS(pair(m, n), ++count);
                }
            }
        }
        cout << count << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
