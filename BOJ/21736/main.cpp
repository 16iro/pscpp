#include <bits/stdc++.h>
using namespace std;

char graph[600][600] = {
    'X',
};
int dx[4] = {0, 1, -1, 0};
int dy[4] = {1, 0, 0, -1};

int BFS(int rn, int rm, int N, int M) {
    int result = 0;
    queue<pair<int, int>> queue;
    queue.push(pair(rn, rm));
    graph[rn][rm] = 'X';
    while (!queue.empty()) {
        pair<int, int> pos = queue.front();
        queue.pop();
        for (int i = 0; i < 4; i++) {
            int nx = clamp(pos.first + dx[i], 0, N - 1);
            int ny = clamp(pos.second + dy[i], 0, M - 1);
            char cell = graph[nx][ny];
            if (cell == 'P') {
                result++;
                cell = 'O';
            }
            if (cell == 'O') {
                graph[nx][ny] = 'X';
                queue.push(pair(nx, ny));
            }
        }
    }
    return result;
}

void solve() {
    int N, M;
    int rn, rm;
    cin >> N >> M;
    for (int n = 0; n < N; n++) {
        string row;
        cin >> row;
        for (int m = 0; m < M; m++) {
            if (row[m] == 'I') {
                rn = n;
                rm = m;
            }
            graph[n][m] = row[m];
        }
    }
    int count = BFS(rn, rm, N, M);
    if (count <= 0)
        cout << "TT";
    else
        cout << count;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
