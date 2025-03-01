基于Flask构建一个Web API应用，环境变量放到.evn

功能一：
1，每天12AM调用/orgs/{org}/copilot/metrics获取数据
2，数据格式见example-response.json
3，返回的数据是一个JSON数组，每一个数据块由日期标识
4，将数组内的每一个数据块以日期作为文件名，保存到Azure Blob
5，对于最近三天的数据，如果Azure Blob中有重名的文件，则对其进行覆盖。如果是更早的数据，则忽略

功能二：
1，实现Get API，根据日期开始和结束参数，从Azure Blob中找到对应的文件
2，将文件内容聚合并返回,格式为JSON