from casatasks import flagmanager, clearcal
import os

# Reset the data to its initial state before we do anything.

def reset_ms(data):
    # Check whether multiple tracks were provided.

    if type(data) == Track:
        tracks = [data]
    elif type(data) == TrackGroup:
        tracks = data.tracks
    else:
        raise ValueError("Data must be a Track or TrackGroup.")

    # Loop through the list and reset.

    for track in tracks:
        if not os.path.exists(track.ms+'.flagversions'):
            flagmanager(vis=track.ms, mode="save", versionname="Original")

        # Clear any calibration that has been done.

        clearcal(vis=track.ms)

        # Remove flagversions that were saved during the previous run.

        flagmanager(vis=track.ms, mode="delete", \
                versionname="PostManualFlagging")
        flagmanager(vis=track.ms, mode="delete", versionname="PreLineFlagging")
        flagmanager(vis=track.ms, mode="delete", versionname="PostLineFlagging")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal1")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal2")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal3")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal4")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal5")
        flagmanager(vis=track.ms, mode="delete", versionname="PostSelfcal6")

        # Restore flags to their original state before doing anything.

        flagmanager(vis=track.ms, mode="restore", versionname="Original")

