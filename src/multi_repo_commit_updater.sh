#!/bin/bash
# 来源:https://github.com/umutphp/github-action-dynamic-profile-page
GITHUB_USERNAME="ChinaGodMan"
REPOSITORIES="UserScripts,gitlens-zh-CN,git-pwsh,github-updater"
README_FILE="README.md"

# 遍历每个仓库
IFS=',' read -ra REPO_LIST <<<"$REPOSITORIES"
for GITHUB_REPO in "${REPO_LIST[@]}"; do
    echo "获取: $GITHUB_REPO"

    # 最新提交信息
    LATEST_COMMIT=$(curl -s -H "Authorization: token $PAT_GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_USERNAME/$GITHUB_REPO/commits/main")
    COMMIT_SHA=$(echo "$LATEST_COMMIT" | grep '"sha"' | head -n 1 | awk -F '"' '{print $4}')
    COMMIT_MESSAGE=$(echo "$LATEST_COMMIT" | grep -oP '"message":\s*"\K[^"]+' | sed 's/\\n.*//')
    COMMIT_URL=$(echo "$LATEST_COMMIT" | grep '"html_url"' | head -n 1 | awk -F '"' '{print $4}')

    # 头部
    REF="refs/heads/main"

    # 插入内容
    INSERTED_LINE="- $GITHUB_USERNAME/$GITHUB_REPO: [$REF@$COMMIT_SHA]($COMMIT_URL) - $COMMIT_MESSAGE"

    # 提取内容
    EXISTING_LINES=$(awk '/<!-- START gadpp -->/{flag=1;next}/<!-- END gadpp -->/{flag=0}flag' "$README_FILE")

    echo "Check result: $RESULT"
    # 检查行存在
    if echo "$EXISTING_LINES" | grep -q "$COMMIT_SHA"; then
        echo "COMMIT_SHA 已存在"
    else
        awk -v insert="$INSERTED_LINE" '
            BEGIN { inside=0 }
            /<!-- START gadpp -->/ { print; print insert; inside=1; next }
            /<!-- END gadpp -->/ { inside=0 }
            { print }
        ' "$README_FILE" >readme_changed.md
        # 更新完成
        mv readme_changed.md "$README_FILE"
        echo "仓库的最新提交已经被更新到 README 文件中。"
    fi

done

# 最大显示数量
MAX_COUNT=5

EXISTING_LINES=$(awk '/<!-- START gadpp -->/{flag=1;next}/<!-- END gadpp -->/{flag=0}flag' "$README_FILE" | head -n $MAX_COUNT)
EXISTING_LINES=$(printf "%s" "$EXISTING_LINES")
sed -i "/<!-- START gadpp -->/,/<!-- END gadpp -->/{
    /<!-- START gadpp -->/{
        n
        r /dev/stdin
        d
    }
    /<!-- END gadpp -->/!d
}" "$README_FILE" <<<"$EXISTING_LINES"
echo "$EXISTING_LINES"
