# Welcome to WWJD! 👋

Hey there! So you've found WWJD (What Was James Doing?) and you're wondering how to get started? You're in the right place! Let's walk through this together.

## First Things First 🚀

You've landed on our GitHub page and you're probably thinking "This looks cool, but how do I actually use it?" Well, let's start from the very beginning.

### 1. Getting the Code

```bash
# Clone the repository
git clone https://github.com/jameswilliamknight/wasdoing.git
cd wasdoing

# Create a symlink for easy access
mkdir -p ~/.local/bin
ln -s "$(pwd)/doc" ~/.local/bin/doc
```

### 2. Initial Setup 🔧

First time? No worries! Let's run the setup wizard:

```bash
doc --setup
```

This will ask you where you want to store your work logs. You can choose:
- Default location (`~/.wwjd/`) - Nice and tidy in your home directory
- Custom location - Maybe you want to keep it with your projects or in a synced folder

### 3. Your First Context 📁

Think of contexts like different notebooks for different projects. Let's create your first one:

```bash
# Create a new context called "my-project"
doc -n my-project

# You'll see something like:
✅ Created new context: my-project
✅ Set my-project as active context
```

### 4. Start Documenting! ✍️

Now the fun part! Let's add some entries:

```bash
# Add what you're working on
doc -H "Starting work on the authentication system"

# Later, add a summary
doc -s "Implemented OAuth2 flow with Google provider"
```

### 5. Viewing Your Work 👀

Your entries are automatically saved and converted to a nice markdown file:

```bash
# List your contexts
doc -l

# Generate documentation (happens automatically)
# The output will be in work_doc.md by default
cat work_doc.md

# Want real-time updates? Use watch mode:
doc -w
```

### 6. Going Pro 🎯

Once you're comfortable with the basics, you might want to try:

- **Multiple Contexts**: Switch between projects with `doc -c project-name`
- **Custom Output**: Save to a different file with `doc -o custom-name.md`
- **PDF Export**: Create PDFs with `doc -e output.pdf`
- **Help**: See all options with `doc --help`

## Common Questions 🤔

**Q: Where's my data stored?**
A: In SQLite databases in your config directory (either `~/.wwjd/tasks/` or your custom location)

**Q: Can I use it for multiple projects?**
A: Absolutely! That's what contexts are for. Create as many as you need.

**Q: I made a mistake, can I edit entries?**
A: Currently, entries are append-only (like a log book). Best practice is to add a new entry with the correction.

## Need Help? 🆘

- Check out our other wiki pages for detailed information
- Open an issue on GitHub if you run into problems
- Join our community discussions

## Next Steps 🎯

Now that you're set up, you might want to:
1. Read about [Working with Contexts](contexts.md)
2. Learn about [Watch Mode](watch-mode.md)
3. Check out the [Project Structure](project-structure.md)

Remember, the goal is to make documenting your work feel natural and easy. Don't worry about getting everything perfect - just start logging what you're doing, and you'll develop a rhythm that works for you!

Happy documenting! 🚀
