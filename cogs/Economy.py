import discord
from discord.ext import commands 
import aiosqlite


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.jobs = {'peasant': 1, 'yard worker': 5, "farmer": 9, "secretary": 11, "military": 15, "dentist": 25}


    @commands.command()
    async def list_jobs(self, ctx):
        em = discord.Embed(title=f"The Availble jobs currently are the following: ")

        for job in self.jobs:
            em.add_field(name=f"{job}", value=f"the income of this job is {self.jobs[job]}", inline=False)

        await ctx.send(embed=em)
        return 


    # a make a people be able to perform jobs 
    # command to select a job
    @commands.command()
    async def select_job(self, ctx, *, job=None):

        if job is None:
            await ctx.send("Please specify a job, if you do not know any use list_jobs to see the full list of jobs available.")    
        else:
            # update the users data in the table, to change the new job
            db = await aiosqlite.connect("ryu.db")
            cursor = await db.execute(f"SELECT job FROM economyTable WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
            result = await cursor.fetchone()
            
            if result is None:
                sql = ("INSERT INTO economyTable (guild_id, user_id, job, wallet, bank) VALUES(?, ?, ?, ?, ?)")
                val = (ctx.guild.id, ctx.author.id, job, 0, 0)
                await db.execute(sql, val)
            else:
                sql = ("UPDATE economyTable SET job = ? WHERE guild_id = ? AND user_id = ?")
                val = (job, ctx.guild.id, ctx.author.id)
                await db.execute(sql, val)
            await db.commit()
            await cursor.close()
            await db.close()

            em = discord.Embed(title=f"You have chosen to work as a {job}")
            await ctx.send(embed=em)
            return 





    # allow the user to get a daily
    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        em = discord.Embed(title=f"You have claimed your daily of 1000 ")
        db = await aiosqlite.connect("ryu.db")

        # update the daily counter by giving the person a 1000
        cursor = await db.execute(f"SELECT wallet FROM economyTable WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        result = await cursor.fetchone()

        if result is None:
            sql = ("INSERT INTO economyTable (guild_id, user_id, job, wallet, bank) VALUES(?, ?, ?, ?, ?)")
            val = (ctx.guild.id, ctx.author.id, "Jobless", 0, 0)
            await db.execute(sql, val)
            await db.execute("UPDATE economyTable SET wallet = wallet + 1000 WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id))
        elif result is not None:
            sql = ("UPDATE economyTable SET wallet = wallet + 1000 WHERE guild_id = ? AND user_id = ?")
            val = (ctx.guild.id, ctx.author.id)
            await db.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()


        await ctx.channel.send(embed=em)
        return 


    @commands.command()
    @commands.cooldown(1, 28800, commands.BucketType.user)
    async def work(self, ctx):
        db = await aiosqlite.connect("ryu.db")
        cursor = await db.execute(f"SELECT job FROM economyTable WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        result = await cursor.fetchone()

        if result is None:
            embed = discord.Embed(titile="You do not have a job selected.")
            await ctx.send(embed=embed)

        else:
            wage = self.jobs[result[0]] * 8 
            sql = ("UPDATE economyTable SET wallet = wallet + ? WHERE guild_id = ? AND user_id = ?")
            val = (wage, ctx.guild.id, ctx.author.id)
            await db.execute(sql, val)
            embed = discord.Embed(title=f"you have earned {wage} today.")
            await ctx.send(embed=embed)
        await db.commit()
        await cursor.close()
        await db.close()
        return 

    # command to depsoti money from your wallet into you bank account
    @commands.command()
    async def dep(self, ctx, *, amount="test"):

        db = await aiosqlite.connect("ryu.db")
        cursor = await db.execute(f"SELECT wallet FROM economyTable WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        result = await cursor.fetchone()

        if result is None:
                embed =  discord.Embed(title=f"You dont have any money to depsit. Go work.")
                await ctx.send(embed=embed)
                return 

        try:
            amt = int(amount)
            if result[0] < amt:
                embed = discord.Embed(title="You do not have that much money.")
                await ctx.send(embed=embed)
                return 
                
            else:
                embed =  discord.Embed(title=f"You have deposited {amt} into your account")
                val = (amt, ctx.guild.id, ctx.author.id)
                await db.execute("UPDATE economyTable SET bank = bank + ? WHERE guild_id = ? AND user_id = ?", val)
                await db.execute("UPDATE economyTable SET wallet = wallet - ? WHERE guild_id = ? AND user_id = ?", val)
                await ctx.send(embed=embed)
                await db.commit()
                await cursor.close()
                await db.close()
                return 

        except ValueError:
            embed =  discord.Embed(title=f"Enter a valid amount of money to deposit.")
            await ctx.send(embed=embed)
            return 

    # command to with draw money from your bank into your wallet for use
    @commands.command()
    async def withdraw(self, ctx, *, amount="test"):

        db = await aiosqlite.connect("ryu.db")
        
        cursor = await db.execute(f"SELECT bank FROM economyTable WHERE guild_id = {ctx.guild.id} AND user_id = {ctx.author.id}")
        result = await cursor.fetchone()

        if result is None:
                embed =  discord.Embed(title=f"You dont have any money to withdraw.")
                await ctx.send(embed=embed)
                return 

        try:
            amt = int(amount)
            if result[0] < amt:
                embed = discord.Embed(title="You do not have that much money.")
                await ctx.send(embed=embed)
                return 
                
            else:
                embed =  discord.Embed(title=f"You have withdrawm {amt} into your account")
                val = (amt, ctx.guild.id, ctx.author.id)
                await db.execute("UPDATE economyTable SET wallet = wallet + ? WHERE guild_id = ? AND user_id = ?", val)
                await db.execute("UPDATE economyTable SET bank = bank - ? WHERE guild_id = ? AND user_id = ?", val)
                await ctx.send(embed=embed)
                await db.commit()
                await cursor.close()
                await db.close()
                return 

        except ValueError:
            embed =  discord.Embed(title=f"Enter a valid amount of money to deposit.")
            await ctx.send(embed=embed)
            return 

    @commands.command()
    async def bal(self, ctx, *, user=None):
        
        if user is None: 
            val = (ctx.guild.id, ctx.author.id)
            db = await aiosqlite.connect("ryu.db")
            cursor = await db.execute("SELECT wallet, bank FROM economyTable WHERE guild_id = ? AND user_id = ?", val)
            result = await cursor.fetchone()


            embed=discord.Embed(title="Your balance is:")
            embed.add_field(name="Wallet", value=result[0], inline=True)
            embed.add_field(name="Bank", value=result[1], inline=True)
            await ctx.send(embed=embed)
        else: 
            await ctx.send("You can only check your own balance")

        return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            time =  "%d:%02d:%02d" % (hour, minutes, seconds)

            msg = f"You are still on cooldown {time}"
            await ctx.send(msg)




def setup(bot):
    bot.add_cog(Economy(bot))