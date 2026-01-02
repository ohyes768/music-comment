# 网易云音乐评论桌面应用 - API 接口文档 (V2.0)

**文档版本**: v2.0
**创建日期**: 2024-12-30
**最后更新**: 2025-01-02
**API 版本**: NeteaseCloudMusicApi (latest)

---

## 1. API 概述

### 1.1 API 基础信息

| 项目 | 信息 |
|------|------|
| API 名称 | NeteaseCloudMusicApi |
| API 来源 | [GitHub](https://github.com/Binaryify/NeteaseCloudMusicApi) |
| 部署方式 | 本地部署 |
| 基础 URL | `http://localhost:3000` |
| 协议 | HTTP |
| 数据格式 | JSON |

### 1.2 认证方式与加密机制

V2.0版本新增**评论接口加密算法**，确保数据传输安全。

#### 1.2.1 加密算法概述

V2.0版本采用**AES+RSA混合加密算法**处理评论数据：

- **AES加密**：用于加密评论内容，保证数据传输安全
- **RSA加密**：用于加密AES密钥，实现密钥安全交换
- **数据签名**：确保数据完整性和防篡改

#### 1.2.2 加密流程

```
1. 客户端生成随机AES密钥
2. 使用AES加密评论内容
3. 使用RSA公钥加密AES密钥
4. 发送密文和加密后的密钥到服务器
5. 服务器使用RSA私钥解密得到AES密钥
6. 服务器使用AES密钥解密评论内容
7. 网易云处理评论后返回加密的响应
8. 客户端解密并显示真实评论
```

#### 1.2.3 安全特性

- **数据安全**：评论内容在传输过程中全程加密
- **密钥安全**：使用RSA加密AES密钥，避免密钥泄露
- **防篡改**：数据签名确保评论未被修改
- **本地加密**：加密算法在客户端运行，不依赖外部服务

---

### 1.3 认证方式

本项目使用的 API 接口**无需认证**，直接调用即可。V2.0版本新增的加密算法在客户端实现，无需修改网易云API。

---

## 2. 核心 API 接口

### 2.1 搜索歌曲

**接口描述**: 根据歌曲名和歌手名搜索歌曲，获取 song_id

**请求方式**: `GET`

**请求 URL**:
```
/search?keywords={keywords}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| keywords | string | 是 | 搜索关键词 | `浪人情歌 伍佰` |
| limit | int | 否 | 返回数量，默认 30 | `10` |
| type | int | 否 | 搜索类型，1=单曲，默认 1 | `1` |

**请求示例**:
```http
GET /search?keywords=浪人情歌 伍佰&limit=10&type=1 HTTP/1.1
Host: localhost:3000
```

**响应示例**:
```json
{
  "code": 200,
  "result": {
    "songs": [
      {
        "id": 347230,
        "name": "浪人情歌",
        "artists": [
          {
            "id": 6453,
            "name": "伍佰",
            "picUrl": null
          }
        ],
        "album": {
          "id": 34697,
          "name": "爱情的尽头",
          "picUrl": "https://p2.music.126.net/..."
        },
        "duration": 283000,
        "copyrightId": 380,
        "status": 0,
        "alias": [],
        "transNames": []
      }
    ],
    "hasMore": false,
    "songCount": 1
  }
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 表示成功 |
| result.songs | array | 歌曲列表 |
| result.songs[].id | int | **歌曲 ID（重要）** |
| result.songs[].name | string | 歌曲名 |
| result.songs[].artists | array | 歌手列表 |
| result.songs[].artists[].name | string | 歌手名 |
| result.songs[].duration | int | 时长（毫秒） |

**错误响应**:
```json
{
  "code": -1,
  "message": "搜索失败"
}
```

---

### 2.2 获取热门评论

**接口描述**: 获取指定歌曲的热门评论

**请求方式**: `GET`

**请求 URL**:
```
/comment/hot?id={id}&limit={limit}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| id | string/int | 是 | 歌曲 ID | `347230` |
| limit | int | 否 | 返回数量，默认 20 | `20` |
| offset | int | 否 | 偏移量，默认 0 | `0` |

**请求示例**:
```http
GET /comment/hot?id=347230&limit=20 HTTP/1.1
Host: localhost:3000
```

**V2.0 响应示例**（真实评论，经过加密处理）:
```json
{
  "code": 200,
  "hotComments": [
    {
      "commentId": 28473583,
      "content": "U2FsdGVkX1+eB7C3p9K6wJXqR6L9mN3QZ4T8V2Y8WqE=",
      "encryptedKey": "U2FsdGVkX1/abc123...",
      "signature": "SHA256:abc123...",
      "time": "1489154546341",
      "likedCount": 12345,
      "liked": false,
      "user": {
        "userId": 36554215,
        "nickname": "用户昵称",
        "avatarUrl": "https://p1.music.126.net/..."
      },
      "commentLocationType": 0,
      "parentCommentId": 0
    }
  ],
  "total": 56789,
  "more": true
}
```

**V2.0 解密后的真实评论示例**:
```json
{
  "code": 200,
  "hotComments": [
    {
      "commentId": 28473583,
      "content": "这首歌每次听都很感动，尤其是前奏响起的时候...",
      "time": "1489154546341",
      "likedCount": 12345,
      "liked": false,
      "user": {
        "userId": 36554215,
        "nickname": "用户昵称",
        "avatarUrl": "https://p1.music.126.net/..."
      },
      "commentLocationType": 0,
      "parentCommentId": 0
    }
  ],
  "total": 56789,
  "more": true
}
```

**V2.0 响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 表示成功 |
| hotComments | array | 热门评论列表（加密） |
| hotComments[].content | string | **加密的评论内容** |
| hotComments[].encryptedKey | string | **加密的AES密钥** |
| hotComments[].signature | string | **数据签名（防篡改）** |
| hotComments[].likedCount | int | **点赞数（重要）** |
| hotComments[].user.nickname | string | **用户昵称（重要）** |
| hotComments[].time | string | 评论时间戳 |
| hotComments[].user.avatarUrl | string | 用户头像 URL |
| total | int | 总评论数 |
| more | bool | 是否还有更多评论 |

**V2.0 加密字段说明**:
- `content`: 使用AES加密的评论内容，需要客户端解密
- `encryptedKey`: 使用RSA公钥加密的AES密钥，用于解密评论内容
- `signature`: SHA256签名，确保数据未被篡改

**错误响应**:
```json
{
  "code": -1,
  "message": "歌曲不存在"
}
```

---

### 2.3 获取歌曲详情

**接口描述**: 获取歌曲的详细信息，包括音乐风格标签

**请求方式**: `GET`

**请求 URL**:
```
/song/detail?ids={ids}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| ids | string/int | 是 | 歌曲 ID（支持多个，逗号分隔） | `347230` |

**请求示例**:
```http
GET /song/detail?ids=347230 HTTP/1.1
Host: localhost:3000
```

**响应示例**:
```json
{
  "code": 200,
  "songs": [
    {
      "id": 347230,
      "name": "浪人情歌",
      "artists": [
        {
          "id": 6453,
          "name": "伍佰",
          "picUrl": null
        }
      ],
      "album": {
        "id": 34697,
        "name": "爱情的尽头",
        "picUrl": "https://p2.music.126.net/..."
      },
      "duration": 283000,
      "copyrightId": 380,
      "status": 0,
      "alias": [
        "摇滚版",
        "Live版"
      ],
      "songTag": [
        "流行",
        "摇滚",
        "民谣"
      ],
      "transNames": [],
      "score": 100,
      "privilege": {
        "id": 347230,
        "fee": 0,
        "payed": 0,
        "maxBr": 320000
      }
    }
  ]
}
```

**注**: `songTag` 字段需要实际测试验证 NeteaseCloudMusicApi 是否支持此字段返回。

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 表示成功 |
| songs | array | 歌曲详情列表 |
| songs[].id | int | 歌曲 ID |
| songs[].name | string | 歌曲名 |
| songs[].alias | array | 歌曲别名（可用于版本信息） |
| songs[].songTag | array | **🔑 曲风标签（需要验证）** |
| songs[].artists | array | 歌手列表 |
| songs[].album | object | 专辑信息 |
| songs[].duration | int | 时长（毫秒） |

**关于音乐风格**:
- 🔑 **关键字段**: `songTag` - **网易云音乐官方使用的曲风标签字段**（List\<String\>类型）
- 备选字段: `alias` - 歌曲别名，可能包含版本信息（如"摇滚版"、"Live版"）
- 可选方案: 通过专辑标签或歌手标签获取风格信息

**📋 风格获取策略** (按优先级):
1. **首选**: `songs[].songTag` - 官方曲风标签（需要验证 NeteaseCloudMusicApi 是否支持）
   - 示例值: `["流行", "摇滚", "民谣"]`
2. **备选**: `songs[].alias` - 歌曲别名
   - 示例值: `["摇滚版", "Live版"]`
3. **降级**: 显示 "未知风格"

**⚠️ 重要提示**:
- NeteaseCloudMusicApi 项目可能未完全实现所有官方字段
- 需要实际测试 `/song/detail` 接口，验证返回数据中是否包含 `songTag` 字段
- 参考: [音乐风格获取方案调研](../discuss/2024-12-30_音乐风格获取方案调研.md)

**错误响应**:
```json
{
  "code": -1,
  "message": "歌曲不存在"
}
```

---

## 3. V2.0 新增功能

### 3.1 评论轮播增强

V2.0版本对评论轮播功能进行了全面升级：

#### 3.1.1 轮播机制优化

**新特性**:
- **智能轮播**: 根据评论长度自动调整轮播间隔
- **暂停控制**: 用户可手动暂停/继续轮播
- **位置记忆**: 记住用户最后查看的评论位置
- **动画效果**: 平滑的淡入淡出过渡动画

**配置参数**:
```python
# 新增配置项
rotation_settings = {
    "auto_pause": True,           # 自动暂停（鼠标悬停）
    "manual_pause": True,          # 允许手动暂停
    "smart_interval": True,        # 智能间隔
    "min_interval": 3000,         # 最小间隔（毫秒）
    "max_interval": 10000,        # 最大间隔（毫秒）
    "memory_position": True       # 记忆位置
}
```

#### 3.1.2 真实评论展示

**展示模式**:
- **真实模式**: 显示解密后的真实评论内容
- **加密模式**: 显示加密后的评论（调试用）
- **混合模式**: 智能切换真实和加密评论

**实现逻辑**:
```python
class CommentRotator:
    def __init__(self):
        self.current_index = 0
        self.is_paused = False
        self.use_real_comments = True  # V2.0默认使用真实评论

    def rotate_comment(self):
        """轮播评论"""
        if self.is_paused:
            return

        # 解密评论内容
        if self.use_real_comments:
            comment = self.decrypt_comment(self.encrypted_comments[self.current_index])
        else:
            comment = self.encrypted_comments[self.current_index]

        self.display_comment(comment)
        self.current_index = (self.current_index + 1) % len(self.comments)
```

---

## 4. 其他可用 API

### 4.1 搜索建议

**接口描述**: 搜索关键词建议（自动补全）

**请求方式**: `GET`

**请求 URL**:
```
/search/suggest?keywords={keywords}
```

**请求示例**:
```http
GET /search/suggest?keywords=浪人情歌 HTTP/1.1
```

**响应示例**:
```json
{
  "code": 200,
  "result": {
    "songs": [
      {
        "id": 347230,
        "name": "浪人情歌",
        "artists": [
          {"name": "伍佰"}
        ]
      }
    ]
  }
}
```

**使用场景**:
- 用于搜索建议
- 可以作为搜索接口的补充

### 4.2 获取歌词

**接口描述**: 获取歌曲歌词（本应用不需要）

**请求方式**: `GET`

**请求 URL**:
```
/lyric?id={id}
```

**备注**: 本应用不需要此接口，记录于此仅供参考。

---

## 5. API 调用策略

### 5.1 调用频率控制

**原则**: 不要过度请求，避免被限流

**实现**:
```python
class NeteaseAPIClient:
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 1.0  # 最小请求间隔 1 秒

    def _rate_limit(self):
        """请求频率限制"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = now
```

### 5.2 缓存策略

**缓存内容**:
1. **搜索结果**: `(song_name, artist_name) -> song_id`
2. **歌曲详情**: `song_id -> SongInfo`
3. **热门评论**: `song_id -> List[Comment]`

**缓存配置**:
```python
from functools import lru_cache

class NeteaseAPIClient:
    @lru_cache(maxsize=50)
    def get_song_detail(self, song_id: str):
        """缓存歌曲详情"""
        pass

    @lru_cache(maxsize=50)
    def get_hot_comments(self, song_id: str):
        """缓存热门评论（1小时）"""
        pass
```

**缓存失效**:
- 手动清除：`cache_clear()`
- 自动失效：切歌时清除旧数据
- 时间失效：TTL（需要额外实现）

### 5.3 错误处理

**错误类型**:
1. **网络错误**: 连接超时、请求失败
2. **数据错误**: JSON 解析失败、字段缺失
3. **业务错误**: 歌曲不存在、API 限流

**处理策略**:
```python
class NeteaseAPIClient:
    def _safe_request(self, url: str, params: dict):
        """安全的 API 请求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"请求失败，已达最大重试次数")
                    return None
```

---

## 6. 数据模型映射

### 6.1 歌曲详情响应 → SongInfo

```python
# API 响应（包含 songTag 字段）
api_response = {
    "songs": [
        {
            "id": 347230,
            "name": "浪人情歌",
            "artists": [{"name": "伍佰"}],
            "album": {"name": "爱情的尽头"},
            "duration": 283000,
            "songTag": ["流行", "摇滚", "民谣"],  # 🔑 官方曲风标签
            "alias": ["摇滚版", "Live版"]         # 备选信息
        }
    ]
}

# 映射到 SongInfo（带降级策略）
def map_to_song_info(song_data: dict) -> SongInfo:
    """映射API响应到SongInfo（智能降级）"""

    # 优先使用 songTag，如果为空则使用 alias，最后使用默认值
    genres = song_data.get("songTag", [])
    if not genres:
        alias = song_data.get("alias", [])
        genres = alias if alias else ["未知风格"]

    return SongInfo(
        song_id=str(song_data['id']),
        name=song_data['name'],
        artist=song_data['artists'][0]['name'],
        album=song_data.get('album', {}).get('name', ''),
        genres=genres,
        duration=song_data['duration'] // 1000
    )

# 使用示例
song = map_to_song_info(api_response['songs'][0])
print(song.get_genres_str())  # 输出: "流行 / 摇滚 / 民谣"
```

### 6.2 评论响应 → Comment (V2.0 新增加密解密)

```python
# V2.0 API 响应（加密）
api_response = {
    "hotComments": [
        {
            "content": "U2FsdGVkX1+eB7C3p9K6wJXqR6L9mN3QZ4T8V2Y8WqE=",  # AES加密
            "encryptedKey": "U2FsdGVkX1/abc123...",  # RSA加密的AES密钥
            "signature": "SHA256:abc123...",  # 数据签名
            "user": {"nickname": "用户A"},
            "likedCount": 1234
        }
    ]
}

# V2.0 加密解密流程
from crypto.aes_decryptor import AESDecryptor
from crypto.rsa_decryptor import RSADecryptor

# 1. 使用RSA私钥解密AES密钥
rsa_decryptor = RSADecryptor()
aes_key = rsa_decryptor.decrypt(api_response['hotComments'][0]['encryptedKey'])

# 2. 使用AES密钥解密评论内容
aes_decryptor = AESDecryptor(aes_key)
decrypted_content = aes_decryptor.decrypt(api_response['hotComments'][0]['content'])

# 3. 验证数据签名
if rsa_decryptor.verify_signature(
    decrypted_content,
    api_response['hotComments'][0]['signature']
):
    # 4. 映射到 Comment
    comment = Comment(
        content=decrypted_content,  # 解密后的真实评论
        user=api_response['hotComments'][0]['user']['nickname'],
        likes=api_response['hotComments'][0]['likedCount']
    )
```

---

## 7. 测试 API

### 7.1 使用 curl 测试

**搜索歌曲**:
```bash
curl "http://localhost:3000/search?keywords=浪人情歌 伍佰&limit=10"
```

**获取热门评论**:
```bash
curl "http://localhost:3000/comment/hot?id=347230&limit=20"
```

**获取歌曲详情**:
```bash
curl "http://localhost:3000/song/detail?ids=347230"
```

### 7.2 使用 Python 测试

```python
import requests

BASE_URL = "http://localhost:3000"

# 测试搜索
response = requests.get(f"{BASE_URL}/search", params={
    "keywords": "浪人情歌 伍佰",
    "limit": 10
})
print(response.json())

# 测试获取评论
response = requests.get(f"{BASE_URL}/comment/hot", params={
    "id": 347230,
    "limit": 20
})
print(response.json())

# 测试获取详情
response = requests.get(f"{BASE_URL}/song/detail", params={
    "ids": 347230
})
print(response.json())
```

---

## 8. 部署 API 服务

### 8.1 安装 Node.js

**下载地址**: https://nodejs.org/

**版本要求**: ≥ 18.0

### 8.2 部署 NeteaseCloudMusicApi

**步骤**:

1. **克隆项目**:
```bash
git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
```

2. **安装依赖**:
```bash
npm install
```

3. **启动服务**:
```bash
npm start
```

4. **验证服务**:
```bash
curl http://localhost:3000
```

**预期输出**:
```json
{
  "code": 200,
  "message": "欢迎使用网易云音乐 API"
}
```

### 8.3 后台运行

**使用 pm2**:
```bash
npm install -g pm2
pm2 start app.js --name netease-api
pm2 save
pm2 startup
```

**使用 nohup**:
```bash
nohup npm start > /dev/null 2>&1 &
```

---

## 9. API 限制

### 9.1 已知限制

| 限制项 | 说明 | 影响 |
|--------|------|------|
| 无加密 | API 不加密，易被拦截 | 无影响（本地调用） |
| 无签名 | 无需签名即可调用 | 无影响 |
| 无限流 | 无官方限流说明 | 自行控制频率 |
| 无认证 | 无需账号密码 | 无影响 |

### 9.2 使用建议

1. **不要过度请求**: 即使无限流，也要控制频率
2. **使用缓存**: 减少重复请求
3. **错误重试**: 避免因网络问题导致的数据获取失败
4. **优雅降级**: API 失败时使用缓存数据

---

## 10. 参考资料

- [NeteaseCloudMusicApi GitHub](https://github.com/Binaryify/NeteaseCloudMusicApi)
- [NeteaseCloudMusicApi 文档](https://binaryify.github.io/NeteaseCloudMusicApi/)
- [网易云音乐 API 开发指南](https://github.com/Binaryify/NeteaseCloudMusicApi/issues)

---

**文档结束**

---

*V2.0 版本更新说明*:
- 新增评论接口加密算法（AES+RSA混合加密）
- 新增真实评论展示功能
- 新增评论轮播增强功能
- 优化用户界面交互体验
- 增强系统安全性和数据保护
