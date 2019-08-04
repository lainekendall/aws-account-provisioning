DescribeStreamResult describeStreamResult = 
    streamsClient.describeStream(new DescribeStreamRequest()
        .withStreamArn("arn:aws:dynamodb:us-east-1:964355697993:table/intern-test-no-space-service-now/stream/2015-07-24T23:54:39.092"));
String streamArn = 
    describeStreamResult.getStreamDescription().getStreamArn();
List<Shard> shards = 
    describeStreamResult.getStreamDescription().getShards();

   for (Shard shard : shards) {
    String shardId = shard.getShardId();
    System.out.println(
        "Processing " + shardId + " from stream "+ streamArn);

    // Get an iterator for the current shard

    GetShardIteratorRequest getShardIteratorRequest = new GetShardIteratorRequest()
        .withStreamArn("arn:aws:dynamodb:us-east-1:964355697993:table/intern-test-no-space-service-now/stream/2015-07-24T23:54:39.092")
        .withShardId(shardId)
        .withShardIteratorType(ShardIteratorType.TRIM_HORIZON);
    GetShardIteratorResult getShardIteratorResult = 
        streamsClient.getShardIterator(getShardIteratorRequest);
    String nextItr = getShardIteratorResult.getShardIterator();

    while (nextItr != null &amp;&amp; numChanges > 0) {
    
        // Use the iterator to read the data records from the shard

        GetRecordsResult getRecordsResult = 
            streamsClient.getRecords(new GetRecordsRequest().
                withShardIterator(nextItr));
        List<Record> records = getRecordsResult.getRecords();
        System.out.println("Getting records...");
        for (Record record : records) {
            System.out.println(record);
            numChanges--;
        }
        nextItr = getRecordsResult.getNextShardIterator();
    }
