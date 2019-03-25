import os
import unittest

import boto3


class TestServerBasic(unittest.TestCase):

    def setUp(self):
        self.boto_kwargs = {
            'region_name': 'us-west-2',
            'aws_access_key_id': 'fake',
            'aws_secret_access_key': 'fake'}

        os.environ['AWS_CA_BUNDLE'] = os.getcwd() + '/certs/bundle'

    def test_basic_ec2(self):
        client = boto3.client('ec2', **self.boto_kwargs)
        self.assertTrue(len(client.describe_instances()['Reservations']) == 0)

    def test_basic_s3(self):
        client = boto3.client('s3', **self.boto_kwargs)
        client.create_bucket(Bucket='test')
        
        self.assertTrue(len(client.list_buckets()['Buckets']) == 1)
