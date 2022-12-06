import asyncio
import json
from typing import NoReturn

import httpx
import pandas

from config import config


class HackerNews:
    def __init__(self) -> NoReturn:
        self.base_url = config.get("HACKERNEWS_BASE_URL")

    @staticmethod
    async def get_response(url: str, client: httpx.AsyncClient, **kwargs):
        response = await client.request(method="GET", url=url, **kwargs)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def to_json(data: dict, filename: str) -> NoReturn:
        print(f"Writing results to file {filename}.json")

        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    async def _send_requests(self, urls: list) -> dict:
        """
        Send a bunch of requests asynchronously

        ids: a list of story ids
        """

        tasks = []

        for url in urls:
            tasks.append(
                asyncio.ensure_future(
                    self.get_response(url, httpx.AsyncClient()))
            )

        results = await asyncio.gather(*tasks)
        return results

    def _get_stories(self, urls: list, count: int) -> dict:
        story_ids = []
        urls = [f"{self.base_url}/{url}" for url in urls]
        all_stories = asyncio.run(self._send_requests(urls))
        for stories in all_stories:
            story_ids.extend(stories[:count])

        if story_ids:
            urls = [f"{self.base_url}/item/{id}.json" for id in story_ids]
            results = asyncio.run(self._send_requests(urls))
            if results:
                data = [
                    {
                        "ID": result.get("id"),
                        "Owner": result.get("by"),
                        "Type": result.get("type"),
                        "Title": result.get("title"),
                        "Body": result.get("text"),
                        "URL": result.get("url"),
                        "Created": result.get("time"),
                    }
                    for result in results
                ]

                return data

    def user_profile(self, id: str) -> dict:
        """
        id: the user's username
        """

        response = httpx.get(f"{self.base_url}/user/{id}.json")
        results = response.json()
        if results:
            # Write to a dataframe
            data = {
                "ID": results.get("id"),
                "Karma": results.get("karma"),
                "About": results.get("about"),
                "Submitted": results.get("submitted")[:5]
                if results.get("submitted")
                else None,
            }

            pandas.set_option("colheader_justify", "center")
            dataframe = pandas.DataFrame([data])
            print("\n\n", dataframe, "\n\n")
            # Write to CSV file
            print(f"Writing results as CSV to file stories.csv")
            dataframe.to_csv(path_or_buf="./stories.csv", index=False)

            # Write to a file
            self.to_json(data=results, filename=f"user-{id}")
        else:
            return {"message": "Invalid or non-exisiting user"}

    def stories(self, count: int = 20) -> dict:
        """
        Returns top 20 stories

        count: number of stories to be returned
        """

        urls = json.loads(config.get("HACKERNEWS_STORIES_URLS"))

        stories = self._get_stories(urls=urls, count=count)
        if stories:
            # Write to a dataframe
            pandas.set_option("colheader_justify", "center")
            dataframe = pandas.concat(
                [pandas.DataFrame(), pandas.DataFrame.from_records(stories)]
            )

            print("\n\n", dataframe, "\n\n")

            # Write to CSV file
            print(f"Writing results as CSV to file stories.csv")
            dataframe.to_csv(path_or_buf="./stories.csv", index=False)

            # Write to JSON file
            self.to_json(data=stories, filename="stories")
        else:
            return {"message": "No stories at the moment"}


hackernews = HackerNews()
hackernews.stories()
