import json
import requests
from uuid import uuid4
from ..archivesspace import ArchivesSpace
from ..models import FileVersion


class DigitalObject(ArchivesSpace):
    """Class for working with Digital Objects in ArchivesSpace."""

    def __init__(self, url="http://localhost:9089", user="admin", password="admin"):
        super().__init__(url, user, password)

    def get_list_of_ids(self, repo_id):
        """Get a list of ids for Digital Objects in a Repository.

        Args:
            repo_id (int): The id of the repository you are querying.

        Returns:
            list: A list of ints that represent each Digital Object in the repository.

        Examples:
            >>> DigitalObject().get_list_of_ids(2)
            []

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects?all_ids=true",
            headers=self.headers,
        )
        return r.json()

    def get_by_page(self, repo_id, page=1, page_size=10):
        """Get Digital Objects on a page.

        Args:
            repo_id (int): The id of the repository you are querying.
            page (int): The page of digital objects you want to get.
            page_size (int): The size of the page you want returned.

        Returns:
            dict: A dict with information about the results plus all matching Digital Objects.

        Examples:
            >>> DigitalObject().get_by_page(2, 2, 10)
            {'first_page': 1, 'last_page': 1, 'this_page': 1, 'total': 0, 'results': []}

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects?page={page}&page_size={page_size}",
            headers=self.headers,
        )
        return r.json()

    def get(self, repo_id, digital_object_id):
        """Get a Resource by id.

        Args:
            repo_id (int): The id of the repository you are querying.
            digital_object_id (int): The id of the digital object you want.

        Returns:
            dict: The digital object as a dict.

        Examples:
            >>> DigitalObject().get(2, 2)
            {'error': 'DigitalObject not found'}

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects/{digital_object_id}",
            headers=self.headers,
        )
        return r.json()

    def create(self, title, repo_id, specified_properties={}, file_versions=[]):
        """Creates a Digital Object in ArchivesSpace using specified properties and defaults.

        Args:
            title (str): A title for your new digital object.
            repo_id (int): The repo_id for the repository of which your digital object belongs.
            specified_properties (dict): Any properties to override properties set in initial object.
            file_versions (list): A list of file versions, if any, to add to your new digital object.

        Returns:
            dict: A dict with information about your new object and whether it was successfully created.

        Examples:
            >>> DigitalObject().create("Test with no versions", 2))
            {'status': 'Created', 'id': 1, 'lock_version': 0, 'stale': None, 'uri': '/repositories/2/digital_objects/1',
            'warnings': []}
            >>> DigitalObject().create("Tulip Tree", 2, file_versions=[FileVersion().add("https://digital.lib.utk.edu/collections/islandora/object/knoxgardens%3A115")])
            {'status': 'Created', 'id': 2, 'lock_version': 0, 'stale': None, 'uri': '/repositories/2/digital_objects/2',
            'warnings': []}

        """
        initial_object = {
            "jsonmodel_type": "digital_object",
            "external_ids": [],
            "subjects": [],
            "linked_events": [],
            "external_documents": [],
            "rights_statements": [],
            "linked_agents": [],
            "is_slug_auto": True,
            "publish": True,
            "file_versions": [],
            "restrictions": False,
            "notes": [],
            "linked_instances": [],
            "title": "Initialized object",
            "digital_object_id": str(uuid4()),
        }
        for key, value in specified_properties.items():
            initial_object[key] = value
        initial_object["title"] = title
        for file_version in file_versions:
            initial_object["file_versions"].append(file_version)
        r = requests.post(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects",
            headers=self.headers,
            data=json.dumps(initial_object),
        )
        return r.json()

    def add_badge(self, repo_id, digital_object_id, badge_uri):
        """Add an image to represent a digital object.

        Args:
            repo_id (int): The id of the repository you are querying.
            digital_object_id (int): The id of the digital object you want.
            badge_uri (str): The uri to image that represents the digital object.

        Returns:
            dict: A message stating whether your badge update was successful or an error.

        Examples
            >>> DigitalObject().add_badge(2, 2, "https://digital.lib.utk.edu/collections/islandora/object/knoxgardens%3A115/datastream/TN")
            {'status': 'Updated', 'id': 2, 'lock_version': 2, 'stale': None, 'uri': '/repositories/2/digital_objects/2',
            'warnings': []}

        """
        current = self.get(repo_id, digital_object_id)
        current["file_versions"].append(
            FileVersion().add(
                badge_uri, show_attribute="embed", is_representative=False
            )
        )
        r = requests.post(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects/{digital_object_id}",
            headers=self.headers,
            data=json.dumps(current),
        )
        return r.json()

    def delete(self, repo_id, digital_object_id):
        """Delete an existing digital object.

        Args:
            repo_id (int): The id of the repository you are querying.
            digital_object_id (int): The id of your digital object.

        Returns:
            dict: A message stating whether your delete was successful or an error.

        Examples:
            >>> DigitalObject(url="http://localhost:8089").create("Test", 2, file_versions=[FileVersion().add('http://localhost:8000/islandora/object/rfta:8')])
            {'status': 'Deleted', 'id': 1}

        """
        r = requests.delete(
            url=f"{self.base_url}/repositories/{repo_id}/digital_objects/{digital_object_id}",
            headers=self.headers,
        )
        return r.json()