from donnees_modeles import *

def lecture_fichier(file_path):
    with open(file_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
        header = lines[0]
        [videos, endpoints, requests, cache_servers, cache_server_capacity] = [int(x) for x in header.split(' ')]
        print('videos {}\n endpoints {} requests {} cache_servers {} cache_server_capacity {}'.format(
            videos, endpoints, requests, cache_servers, cache_server_capacity
        ))

        video_sizes = lines[1]
        video_list = [Videos(i, int(x)) for (i, x) in enumerate(video_sizes.split(' '))]

        cache_servers = [Cache_Serveur(i, cache_server_capacity) for i in range(cache_servers)]

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

            endpoint = Endpoints(i, latency_to_datacenter, connected_caches)

            for connected_cache in connected_caches:
                cache_servers[connected_cache['cache_id']].append_endpoint(endpoint)

            endpoint_list.append(endpoint)

        request_list = []
        for request_line in lines[current_index:]:
            [video_id, endpoint_id, number_of_requests] = [int(x) for x in request_line.split(' ')]
            request = Requetes(video_id, endpoint_id, number_of_requests)
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

        return DonneesLus(cache_server_capacity,video_list,endpoint_list,cache_servers,request_list)





def ecriture_fichier(cache_servers, filename):
    cache_server_we_use = [cache_server for cache_server in cache_servers if len(cache_server.videos) > 0]
    with open(filename, 'w') as file_out:
        file_out.write('{}\n'.format(len(cache_server_we_use)))
        for cache_server in cache_server_we_use:
            videos_string = ' '.join([str(video.id) for video in cache_server.videos])
            file_out.write('{} {}\n'.format(cache_server.id, videos_string))