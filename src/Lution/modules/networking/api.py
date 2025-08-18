"""A class that stores API endpoints."""

from typing import Optional


class Api:
    """
    A class that stores API endpoints.

    Classes:
        GitHub: Stores all GitHub API endpoints.
        Roblox: Stores all Roblox API endpoints.
    """

    # region GitHub
    class GitHub:
        """
        Stores all GitHub API endpoints.
        
        Attributes:
            LATEST_VERSION (str): Stores the API endpoint to retrieve the latest version of this program.
            RELEASE_INFO (str): Store the API endpoint to retrieve information on the latest release.
            MOD_GENERATOR_BLACKLIST (str): Stores the API endpoint to retrieve a list of icons that are to be ignored by the mod generator.
        """

        LATEST_VERSION: str = r"https://raw.githubusercontent.com/TheKliko/klikos-modding-tool/refs/heads/version-2.0.0/GitHub%20Files/version.json"
        LATEST_RELEASE_INFO: str = r"https://api.github.com/repos/TheKliko/klikos-modding-tool/releases/latest"
        MOD_GENERATOR_CONFIG: str = r"https://raw.githubusercontent.com/klikos-modloader/config/refs/heads/main/mod_generator.json"
    # endregion

    # region Roblox
    class Roblox:
        """
        Stores all Roblox API endpoints.
        
        Classes:
            Deployment: Stores all Roblox API endpoints related to getting the latest deployment.
            Activity: Stores all Roblox API endpoints related to Discord RPC.
        """

        # region Deployment
        class Deployment:
            """
            Stores all Roblox API endpoints related to getting the latest deployment.
            
            Attributes:
                HISTORY (str): Stores the API endpoint to retrieve Roblox's deploy history.
            
            Methods:
                channel(binary_type: str) -> str:
                    Returns the API endpoint to retrieve the user's deployment channel.
                latest(binary_type: str, channel: Optional[str] = None) -> str:
                    Returns the API endpoint to retrieve the latest Roblox version.
                manifest(version_guid: str) -> str:
                    Returns the API endpoint to retrieve the package manifest.
                download(version_guid: str, file: str) -> str:
                    Returns the download URL for the given file.
            """
            
            HISTORY: str = r"https://setup.rbxcdn.com/DeployHistory.txt"

            @staticmethod
            def channel(binary_type: str) -> str:
                """
                Returns the API endpoint to retrieve the user's deployment channel.

                Parameters:
                    binary_type (str): The binary type (example: "WindowsPlayer", "WindowsStudio64").

                Returns:
                    str: The URL for the deployment channel API endpoint.
                """

                return rf"https://clientsettings.roblox.com/v2/user-channel?binaryType={binary_type}"

            @staticmethod
            def latest(binary_type: str, channel: Optional[str] = None) -> str:
                """
                Returns the API endpoint to retrieve the latest Roblox version.

                Parameters:
                    binary_type (str): The binary type (example: "WindowsPlayer", "WindowsStudio64").
                    channel (Optional[str]): The user's deployment channel (example: "LIVE").

                Returns:
                    str: The URL for the version API endpoint.
                """

                if channel is None:
                    return rf"https://clientsettingscdn.roblox.com/v2/client-version/{binary_type}"
                return rf"https://clientsettingscdn.roblox.com/v2/client-version/{binary_type}/channel/{channel}"

            @staticmethod
            def manifest(version_guid: str) -> str:
                """
                Returns the API endpoint to retrieve the package manifest.

                Parameters:
                    version_guid (str): The GUID of the user's Roblox version.

                Returns:
                    str: The URL for the package manifest API endpoint.
                """

                return rf"https://setup.rbxcdn.com/{version_guid}-rbxPkgManifest.txt"

            @staticmethod
            def download(version_guid: str, file: str) -> str:
                """
                Returns the download URL for the given file.

                Parameters:
                    version_guid (str): The GUID of the user's Roblox version.
                    file (str): The file to download.

                Returns:
                    str: The URL for downloading the given file for the given Roblox version.
                """

                return rf"https://setup.rbxcdn.com/{version_guid}-{file}"
        # endregion

        # region Activity
        class Activity:
            """
            Stores all Roblox API endpoints related to Discord RPC.
            
            Methods:
                universe_id(place_id: str) -> str:
                    Returns the API endpoint to retrieve the universe ID of the specified game.
                game(universe_id: str) -> str:
                    Returns the API endpoint to retrieve information on the specified game.
                thumbnail(universe_id: str, size: str = "512x512", circular: bool = False) -> str:
                    Returns the API endpoint to retrieve the thumbnail of the specified game.
            """

            @staticmethod
            def universe_id(place_id: str) -> str:
                """
                Returns the API endpoint to retrieve the universe ID of the specified game.

                Parameters:
                    place_id (str): The ID of the Roblox place.

                Returns:
                    str: The URL for the universe ID API endpoint.
                """

                return rf"https://apis.roblox.com/universes/v1/places/{place_id}/universe"

            @staticmethod
            def game(universe_id: str) -> str:
                """
                Returns the API endpoint to retrieve information on the specified game.

                Parameters:
                    universe_id (str): The ID of the Roblox universe.

                Returns:
                    str: The URL for the game info API endpoint.
                """

                return rf"https://games.roblox.com/v1/games?universeIds={universe_id}"

            @staticmethod
            def thumbnail(universe_id: str, size: str = "512x512", circular: bool = False) -> str:
                """
                Returns the API endpoint to retrieve the thumbnail of the specified game.

                Parameters:
                    universe_id (str): The ID of the Roblox universe.
                    size (str): The size of the thumbnail (example: "512x512").
                    circular (bool): Whether the thumbnail should be circular.

                Returns:
                    str: The URL for the game thumbnail API endpoint.
                """
                
                return rf"https://thumbnails.roblox.com/v1/games/icons?universeIds={universe_id}&returnPolicy=PlaceHolder&size={size}&format=Png&isCircular={str(circular).lower()}"
        # endregion
    # endregion