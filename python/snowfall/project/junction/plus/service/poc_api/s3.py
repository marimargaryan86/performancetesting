import boto3


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
    ) -> None:
        self._client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def put(self, body: bytes, bucket: str, name: str) -> None:
        self._client.put_object(
            Body=body,
            Bucket=bucket,
            Key=name,
            ContentType="image/png",
        )

    def delete(self, bucket: str, name: str) -> None:
        self._client.delete_object(Bucket=bucket, Key=name)
