#include <iostream>
#include <vector>
#include <math.h>
#include <algorithm>
using namespace std;

int calculateLastRow(int x,int y,int k,vector<vector<char>>&matrix,int m)
{
    int currentPathLength1 = 0;

    int ileWybrzuenLeft = k;

    for(int i=x;i<m;i++)
    {
        if(matrix[y][i]=='@'){
            if(ileWybrzuenLeft >0)
            {
                ileWybrzuenLeft --;

            }
            else{
                break;
            }
        }
        else{
            currentPathLength1++;
        }


    }

    ileWybrzuenLeft = k;
    int currentPathLength2 = 0;
    for(int i = x;i>=0;i--)
    {
        if(matrix[y][i]=='@'){
            if(ileWybrzuenLeft >0)
            {
                ileWybrzuenLeft --;
            }
            else{
                break;
            }
        }
        else{
            currentPathLength2++;
        }
    }
    return max(currentPathLength2,currentPathLength1);
}
int calculateMaxLength(int x,int y,int k,vector<vector<char>>&matrix,vector<vector<vector<int>>>&dp,int m)
{
    int currentLength =0;
    int maxLength = 0 ;

    int pozostaleWyburzenia = k;
    for(int i=x;i<m;i++)
    {
        if(matrix[y][i]=='@')
        {
            if(pozostaleWyburzenia==0){
                break;
            }
            else{
                pozostaleWyburzenia--;
            }
        }
        else{
            currentLength++;
        }


        int bottomValue = dp[y+1][i][pozostaleWyburzenia];
        maxLength = max(maxLength,bottomValue+currentLength);

    }
    pozostaleWyburzenia = k;
    currentLength = 0;
    for(int i=x;i>=0;i--)
    {
        if(matrix[y][i]=='@')
        {
            if(pozostaleWyburzenia==0){
                break;
            }
            else{
                pozostaleWyburzenia--;
            }
        }
        else{
            currentLength++;
        }


        int bottomValue = dp[y+1][i][pozostaleWyburzenia];
        maxLength = max(maxLength,bottomValue+currentLength);

    }
    return maxLength;
}
void generatePath(vector<vector<bool>>&visited,vector<pair<int,int>>&path,vector<vector<char>>&matrix,vector<vector<vector<int>>>&dp,int k,int x,int y,int pathLength,int cols,int rows,bool &pathFound)
{
    if(pathFound)return;

    if(pathLength==0)
    {
        path.push_back({x,y});
        pathFound=true;
        return;
    }

    int dirX[] = {0,-1,1};
    int dirY[] = {1,0,0};

    path.push_back({x,y});
    visited[y][x]=1;
    for(int i=0;i<3;i++)
    {
        int newX = x + dirX[i];
        int newY = y + dirY[i];

        if(newX>=0 && newX < cols&& newY>=0 && newY < rows&& dp[newY][newX][k]>=pathLength&&!visited[newY][newX])
        {
            if(matrix[newY][newX] == '@')
            {
                generatePath(visited,path,matrix,dp,k-1,newX,newY,pathLength,cols,rows,pathFound);
            }
            else{
                generatePath(visited,path,matrix,dp,k,newX,newY,pathLength-1,cols,rows,pathFound);
            }
        }
    }
    visited[y][x]=0;
}
int main()
{
    ios_base::sync_with_stdio(0);
    cin.tie(0);
    int k;
    cin>>k;
    int n,m;
    cin>>n>>m;
    vector<vector<char>>matrix(n,vector<char>(m,'.'));
    int startX=0,startY=0;
    for(int i=0;i<n;i++)
    {
        for(int j=0;j<m;j++)
        {
            char c;
            cin>>c;
            matrix[i][j] = c;
            if(c =='S')
            {
                startX = j;
                startY = i;
            }
        }
    }
    int tryb;
    cin>>tryb;

    vector<vector<vector<int>>>dp(n,vector<vector<int>>(m,vector<int>(k+1,0)));

    for(int i=0;i<m;i++)
    {
        for(int j=0;j<=k;j++)
        {
                dp[n-1][i][j] = calculateLastRow(i,n-1,j,matrix,m);


        }

    }
    for(int y=n-2;y>=startY;y--)
    {
        for(int x=0;x<m;x++)
        {
            for(int j = 0;j<=k;j++)
            {

                    dp[y][x][j] = calculateMaxLength(x,y,j,matrix,dp,m);


            }

        }
    }


    if(tryb==1)
    {
        vector<pair<int,int>>path;
        vector<vector<bool>>visited(n,vector<bool>(m,0));
        bool pathFound = false;
        generatePath(visited,path,matrix,dp,k,startX,startY,dp[startY][startX][k]-1,m,n,pathFound);


        for(int i=path.size()-1;i>0;i--)
        {
            int currentX = path[i].first;
            int currentY = path[i].second;

            int previousX = path[i-1].first;
            int previousY = path[i-1].second;

            if(currentX - previousX ==1 )
            {
                matrix[currentY][currentX] = 'L';
            }
            else if(currentX - previousX == -1 )
            {
                matrix[currentY][currentX] = 'R';
            }
            else if(currentY - previousY== 1)
            {
                matrix[currentY][currentX] = 'U';
            }

        }
    }


    cout<<dp[startY][startX][k]-1<<endl;
    if(tryb==1)
    {
        for(int i=0;i<n;i++)
        {
            for(int j=0;j<m;j++)
            {
                cout<<matrix[i][j];
            }
            cout<<endl;
        }

    }

    return 0;
}

