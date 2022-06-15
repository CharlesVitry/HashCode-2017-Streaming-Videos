import sys

class Video(object):
    """A video to be cached"""

    def __init__(self, id, size):
        self.id = id
        self.requests = []
        self.popularity_per_endpoint_cache = {}
        self.popularity_per_endpoint_cache_norm = {}
        self.size_norm = None
        self.size = size

    def __str__(self):
        return '{} - size({}) request({})'.format(self.id, self.size, len(self.requests))

    def __repr__(self):
        return self.__str__()

    def append_request(self, request):
        self.requests.append(request)

    def ratio_endpoint(self, endpoint_id):
        return self.popularity_per_endpoint(endpoint_id) / self.size

    def ratio_endpoint_norm(self, endpoint_id):
        return self.popularity_per_endpoint_norm(endpoint_id) / self.size

    def normalize_size(self, videos_size):
        self.size_norm = (self.size / videos_size)

    def popularity(self):
        return sum([request.number_of_requests for request in self.requests])

    def popularity_per_endpoint(self, endpoint_id):
        if endpoint_id in self.popularity_per_endpoint_cache:
            return self.popularity_per_endpoint_cache[endpoint_id]
        result = sum([request.number_of_requests for request in self.requests if request.endpoint_id == endpoint_id])
        self.popularity_per_endpoint_cache[endpoint_id] = result
        return result

    def popularity_per_endpoint_norm(self, endpoint_id):
        if endpoint_id in self.popularity_per_endpoint_cache_norm:
            return self.popularity_per_endpoint_cache_norm[endpoint_id]
        result = sum([request.number_of_requests_norm for request in self.requests if request.endpoint_id == endpoint_id])
        self.popularity_per_endpoint_cache_norm[endpoint_id] = result
        return result

class Endpoint(object):

    def __init__(self, id, latency_to_datacenter, cache_servers_with_latency):
        self.id = id
        self.requests = []
        self.cache_servers_with_latency_norm = []
        self.get_cache_server_latency_norm_cache = {}
        self.latency_to_datacenter_norm = None
        self.latency_to_datacenter = latency_to_datacenter
        self.cache_servers_with_latency = cache_servers_with_latency

    def __str__(self):
        return '{} - latency({}) caches({}) requests({})'\
            .format(self.id, self.latency_to_datacenter, len(self.cache_servers_with_latency), len(self.requests))

    def __repr__(self):
        return self.__str__()

    def normalize_latency(self, latency_sum):
        self.latency_to_datacenter_norm = self.latency_to_datacenter / latency_sum
        for cache_server in self.cache_servers_with_latency:
            self.cache_servers_with_latency_norm.append({
                'cache_id': cache_server['cache_id'],
                'latency_norm': cache_server['latency'] / latency_sum
            })

    def get_cache_server_latency (self, cache_server_id):
        return [cache_server['latency'] for cache_server in self.cache_servers_with_latency if cache_server_id == cache_server['cache_id']][0]

    def get_cache_server_latency_norm (self, cache_server_id):
        if cache_server_id in self.get_cache_server_latency_norm_cache:
            return self.get_cache_server_latency_norm_cache[cache_server_id]
        result = [cache_server['latency_norm'] for cache_server in self.cache_servers_with_latency_norm if cache_server_id == cache_server['cache_id']][0]
        self.get_cache_server_latency_norm_cache[cache_server_id] = result
        return result

    def remove_requests(self, video_id):
        self.requests = [request for request in self.requests if request.video_id != video_id]

    def append_request(self, request):
        self.requests.append(request)

class CacheServer(object):

    def __init__(self, id, size):
        self.id = id
        self.endpoints = []
        self.videos = []
        self.size = size

    def __str__(self):
        return '{} - size({})'\
            .format(self.id, self.size)

    def __repr__(self):
        return self.__str__()

    def append_endpoint(self, endpoint):

        self.endpoints.append(endpoint)

    def append_video(self, video):
        self.videos.append(video)

    def score(self, videos):
        result = 0
        for endpoint in self.endpoints:
            # print('endpoint {} {}'.format(endpoint.id, len(self.endpoints)), flush=True)
            videos_ratio = 0
            for request in endpoint.requests:
                video = videos[request.video_id]
                videos_ratio += video.ratio_endpoint_norm(endpoint.id)
            result += (endpoint.latency_to_datacenter_norm - endpoint.get_cache_server_latency_norm(self.id)) * videos_ratio
        return result

class Request(object):

    def __init__(self, video_id, endpoint_id, number_of_requests):
        self.video_id = video_id
        self.endpoint_id = endpoint_id
        self.number_of_requests_norm = None
        self.number_of_requests = number_of_requests

    def __str__(self):
        return 'video({}) endpoint({}) requests({})'\
            .format(self.video_id, self.endpoint_id, self.number_of_requests)

    def __repr__(self):
        return self.__str__()

    def normalize_number_of_requests(self, request_sum):
        self.number_of_requests_norm = self.number_of_requests / request_sum

def normalize(values):
    sum_values = sum(values)
    return [value/sum_values for value in values]


def solve(videos, endpoints, requests, cache_servers, cache_server_capacity):
    print('start sorting servers')
    sorted_cache_servers = sorted(cache_servers, key=lambda c: -c.score(videos))
    # sorted_cache_servers = cache_servers
    print('finish sorting servers')
    # print(sorted_cache_servers, [c.score(videos) for c in sorted_cache_servers])
    for cache_server in sorted_cache_servers:
        print('{} {}'.format(cache_server.id, len(cache_servers)), sep=' ', end='', flush=True)
        video_sum = 0
        video_score = {}
        for endpoint in cache_server.endpoints:
            for request in endpoint.requests:
                video = videos[request.video_id]
                result = (
                    endpoint.latency_to_datacenter_norm - endpoint.get_cache_server_latency_norm(cache_server.id)
                ) * video.ratio_endpoint_norm(endpoint.id)
                if request.video_id in video_score:
                    video_score[request.video_id] += result
                else:
                    video_score[request.video_id] = result
        video_score_enumerated = video_score.items()
        sorted_video_score_enumerated = sorted(video_score_enumerated, key=lambda x: -x[1])

        cache_filled_status = 0
        # print(video_score)
        for (index, score) in sorted_video_score_enumerated:
            if score == 0:
                break
            video = videos[index]
            if (cache_filled_status + video.size > cache_server.size):
                continue
            cache_filled_status += video.size
            cache_server.append_video(video)
            for endpoint in cache_server.endpoints:
                endpoint.remove_requests(video.id)

    return cache_servers


def read_file(file_path):
    """Read input file"""
    with open(file_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
        header = lines[0]
        [videos, endpoints, requests, cache_servers, cache_server_capacity] = [int(x) for x in header.split(' ')]
        print('videos {}\n endpoints {} requests {} cache_servers {} cache_server_capacity {}'.format(
            videos, endpoints, requests, cache_servers, cache_server_capacity
        ))

        video_sizes = lines[1]
        video_list = [Video(i, int(x)) for (i, x) in enumerate(video_sizes.split(' '))]

        cache_servers = [CacheServer(i, cache_server_capacity) for i in range(cache_servers)]

        endpoint_list = []
        # keeps track of the last index, which is needed for the video parsing
        current_index = 2
        for i in range(endpoints):
            # we start from the second line
            current_endpoint = lines[current_index]
            [latency_to_datacenter, number_of_connected_caches] = [int(x) for x in current_endpoint.split(' ')]
            current_index += 1
            connected_caches = []
            for connected_cache_line in lines[current_index:(current_index + number_of_connected_caches)]:
                [cache_id, latency] = [int(x) for x in connected_cache_line.split(' ')]
                connected_caches.append({
                    'cache_id': cache_id,
                    'latency': latency
                })
                current_index += 1

            endpoint = Endpoint(i, latency_to_datacenter, connected_caches)

            for connected_cache in connected_caches:
                cache_servers[connected_cache['cache_id']].append_endpoint(endpoint)

            endpoint_list.append(endpoint)

        request_list = []
        for request_line in lines[current_index:]:
            [video_id, endpoint_id, number_of_requests] = [int(x) for x in request_line.split(' ')]
            request = Request(video_id, endpoint_id, number_of_requests)
            video = video_list[video_id]
            if video.size <= cache_server_capacity:
                video.append_request(request)
            endpoint_list[endpoint_id].append_request(request)
            request_list.append(request)

        # normalize endpoints latency to datacenter
        print('normalize endpoints')
        latency_sum = sum([endpoint.latency_to_datacenter for endpoint in endpoint_list])
        for endpoint in endpoint_list:
            endpoint.normalize_latency(latency_sum)

        # normalize videos
        print('normalize videos')
        videos_size_sum = sum([video.size for video in video_list])
        for video in video_list:
            video.normalize_size(videos_size_sum)

        # normalize popularity of videos
        print('normalize requests')
        request_sum = sum([request.number_of_requests for request in request_list])
        for request in request_list:
            request.normalize_number_of_requests(request_sum)
        print('finished normalizing')

        return {
            'videos': video_list,
            'endpoints': endpoint_list,
            'requests': request_list,
            'cache_server_capacity': cache_server_capacity,
            'cache_servers': cache_servers
        }

def write_file(cache_servers, filename):
    """Write output file."""
    cache_server_we_use = [cache_server for cache_server in cache_servers if len(cache_server.videos) > 0]
    with open(filename, 'w') as file_out:
        file_out.write('{}\n'.format(len(cache_server_we_use)))
        for cache_server in cache_server_we_use:
            videos_string = ' '.join([str(video.id) for video in cache_server.videos])
            file_out.write('{} {}\n'.format(cache_server.id, videos_string))


def main():
    """Main function."""

    if len(sys.argv) < 3:
        sys.exit('Syntax: %s <filename> <output>' % sys.argv[0])

    result = read_file(sys.argv[1])
    cache_server = solve(result['videos'], result['endpoints'], result['requests'], result['cache_servers'], result['cache_server_capacity'])
    write_file(cache_server, sys.argv[2])


if __name__ == '__main__':
    print('HASHCODE - TU_DUDES')
    print('running python {}'.format(sys.version_info.major))
    main()
    # result = read_file('example.in')
    # # print(result)
    # cache_servers = solve(result['videos'], result['endpoints'], result['requests'], result['cache_servers'], result['cache_server_capacity'])
    # # print([cache_server.videos for cache_server in cache_servers])
    # write_file(cache_servers, 'wurst.out')

