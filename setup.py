import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='BaboonTracking',
        version='0.2dev',
        packages=['baboon_tracking', 'baboon_tracking.registration', 'baboon_tracking.foreground_extraction', 'baboon_tracking.blob_detection', 'baboon_tracking.object_tracking'],
        author='Anh Ngo',
        author_email='adn057@ucsd.edu',
        description='A package to interchangeably test image detection and tracking methods/algorthms/implementations',
        long_description=long_description,
        url='https://github.com/UCSD-E4E/baboon-tracking',
        license='MIT',
)
